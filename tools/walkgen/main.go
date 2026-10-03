// walkgen renders a deterministic drunkard's-walk glyph field for each post,
// as transparent PNGs in light and dark ink. The walk is seeded from the
// post's filename slug, so a post's art never changes between runs.
//
// The look is a halftone of rings: a long walk's visit counts are blurred
// into smooth density, then every cell gets a mark from a weight ramp, so
// valleys read as faint specks and dots, the mid field as a lattice of thin
// and bold rings, the busy ground as targets, and the walk's favorite places
// as solid discs. The marks are drawn as geometry rather than font glyphs,
// so their size and weight are exact.
package main

import (
	"flag"
	"fmt"
	"hash/fnv"
	"image"
	"image/color"
	"image/png"
	"log"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const (
	gridW = 54
	gridH = 27
	steps = 45000

	// Rendered at 2x and displayed at half size, so the display width is
	// gridW * cellPx / 2, just inside the 648px column.
	cellPx = 24
)

var (
	lightInk = color.NRGBA{R: 0x56, G: 0x56, B: 0x56} // --fg-quiet, light
	darkInk  = color.NRGBA{R: 0xa3, G: 0xa7, B: 0xae} // --fg-quiet, dark
)

// shape reports whether a point in cell pixels is inked.
type shape func(x, y float64) bool

// disc is a filled circle of radius r at the cell's center.
func disc(r float64) shape {
	return func(x, y float64) bool { return math.Hypot(x-cellPx/2, y-cellPx/2) < r }
}

// ring is a circle of radius r drawn with stroke width w at the cell's center.
func ring(r, w float64) shape {
	return func(x, y float64) bool {
		return math.Abs(math.Hypot(x-cellPx/2, y-cellPx/2)-r) < w/2
	}
}

// mark is one step of the density ramp: the union of its shapes, inked at
// alpha. Lower weights get lighter alpha as well as thinner shapes, so the
// tonal range survives in a single ink over both backgrounds.
type mark struct {
	shapes []shape
	alpha  float64
}

const c = cellPx

var ramp = []mark{
	{shapes: []shape{disc(c * 0.07)}, alpha: 0.35},
	{shapes: []shape{disc(c * 0.16)}, alpha: 0.50},
	{shapes: []shape{ring(c*0.36, c*0.09)}, alpha: 0.58},
	{shapes: []shape{ring(c*0.36, c*0.18)}, alpha: 0.70},
	{shapes: []shape{ring(c*0.38, c*0.16), disc(c * 0.14)}, alpha: 0.82},
	{shapes: []shape{disc(c * 0.47)}, alpha: 1},
}

// Cumulative area cuts on the shaded value; one fewer than ramp entries.
// Weighted so the ring lattice carries the field, targets gather into
// continents and solid discs stay rare.
var cuts = []float64{0.08, 0.22, 0.46, 0.76, 0.975}

// coverage rasterizes a mark into a cell-sized alpha mask, supersampling
// each pixel 4x4 so the curves are antialiased.
func (m mark) coverage() []float64 {
	const ss = 4
	a := make([]float64, cellPx*cellPx)
	for py := range cellPx {
		for px := range cellPx {
			hits := 0
			for sy := range ss {
				for sx := range ss {
					x := float64(px) + (float64(sx)+0.5)/ss
					y := float64(py) + (float64(sy)+0.5)/ss
					for _, s := range m.shapes {
						if s(x, y) {
							hits++
							break
						}
					}
				}
			}
			a[py*cellPx+px] = m.alpha * float64(hits) / (ss * ss)
		}
	}
	return a
}

// lcg is a small deterministic PRNG (Numerical Recipes constants). Stability
// matters more than quality here: the same slug must draw the same walk on
// every machine forever.
type lcg struct{ s uint32 }

func (r *lcg) next() uint32 {
	r.s = r.s*1664525 + 1013904223
	return r.s >> 16
}

func walk(slug string) [][]float64 {
	h := fnv.New32a()
	h.Write([]byte(slug))
	rng := &lcg{s: h.Sum32()}

	visits := make([][]float64, gridH)
	for y := range visits {
		visits[y] = make([]float64, gridW)
	}
	x, y := gridW/2, gridH/2

	for range steps {
		dx, dy := 0, 0
		switch rng.next() % 4 {
		case 0:
			dx = 1
		case 1:
			dx = -1
		case 2:
			dy = 1
		case 3:
			dy = -1
		}
		// Bounce off the walls rather than clamp, so the borders don't
		// accumulate artificial density.
		if nx := x + dx; nx < 0 || nx >= gridW {
			dx = -dx
		}
		if ny := y + dy; ny < 0 || ny >= gridH {
			dy = -dy
		}
		x += dx
		y += dy
		visits[y][x]++
	}
	return visits
}

// blur runs a 3x3 box blur with edge clamping, smoothing walk speckle into
// the continents that give the field its shape.
func blur(g [][]float64, passes int) [][]float64 {
	for range passes {
		out := make([][]float64, gridH)
		for y := range out {
			out[y] = make([]float64, gridW)
			for x := range out[y] {
				sum, n := 0.0, 0
				for dy := -1; dy <= 1; dy++ {
					for dx := -1; dx <= 1; dx++ {
						yy, xx := y+dy, x+dx
						if yy < 0 || yy >= gridH || xx < 0 || xx >= gridW {
							continue
						}
						sum += g[yy][xx]
						n++
					}
				}
				out[y][x] = sum / float64(n)
			}
		}
		g = out
	}
	return g
}

// shade maps blurred density to ramp levels. Straight max-normalization put
// nearly the whole field in one band, because a walk's density is peaky; the
// equalized component spreads tones across the image, the raw component
// keeps calm posts calmer than stormy ones, and a seeded dither roughens
// region borders so they do not read as flat contours.
func shade(g [][]float64, slug string) [][]int {
	all := make([]float64, 0, gridW*gridH)
	max := 0.0
	for y := range gridH {
		for x := range gridW {
			all = append(all, g[y][x])
			if g[y][x] > max {
				max = g[y][x]
			}
		}
	}
	sort.Float64s(all)

	h := fnv.New32a()
	h.Write([]byte(slug + "/dither"))
	rng := &lcg{s: h.Sum32()}

	lv := make([][]int, gridH)
	for y := range lv {
		lv[y] = make([]int, gridW)
		for x := range lv[y] {
			eq := float64(sort.SearchFloat64s(all, g[y][x])) / float64(len(all))
			raw := 0.0
			if max > 0 {
				raw = g[y][x] / max
			}
			v := 0.55*eq + 0.45*raw
			v += (float64(rng.next()%1000)/1000 - 0.5) * 0.04
			l := 0
			for _, c := range cuts {
				if v >= c {
					l++
				}
			}
			lv[y][x] = l
		}
	}
	return lv
}

func render(lv [][]int, ink color.NRGBA, masks [][]float64) *image.NRGBA {
	img := image.NewNRGBA(image.Rect(0, 0, gridW*cellPx, gridH*cellPx))
	for y := range gridH {
		for x := range gridW {
			mask := masks[lv[y][x]]
			for py := range cellPx {
				for px := range cellPx {
					if a := mask[py*cellPx+px]; a > 0 {
						c := ink
						c.A = uint8(a*255 + 0.5)
						img.SetNRGBA(x*cellPx+px, y*cellPx+py, c)
					}
				}
			}
		}
	}
	return img
}

func writePNG(path string, img *image.NRGBA) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	return png.Encode(f, img)
}

func main() {
	contentDir := flag.String("content", "content/posts", "directory of post markdown files")
	outDir := flag.String("out", "static/_Images/walks", "output directory for PNGs")
	flag.Parse()

	masks := make([][]float64, len(ramp))
	for i, m := range ramp {
		masks[i] = m.coverage()
	}

	if err := os.MkdirAll(*outDir, 0o755); err != nil {
		log.Fatal(err)
	}

	posts, err := filepath.Glob(filepath.Join(*contentDir, "*.md"))
	if err != nil {
		log.Fatal(err)
	}

	n := 0
	for _, p := range posts {
		slug := strings.TrimSuffix(filepath.Base(p), ".md")
		if strings.HasPrefix(slug, "_") {
			continue
		}
		lv := shade(blur(walk(slug), 2), slug)
		if err := writePNG(filepath.Join(*outDir, slug+"-light.png"), render(lv, lightInk, masks)); err != nil {
			log.Fatal(err)
		}
		if err := writePNG(filepath.Join(*outDir, slug+"-dark.png"), render(lv, darkInk, masks)); err != nil {
			log.Fatal(err)
		}
		n++
	}
	fmt.Printf("generated %d walks in %s\n", n, *outDir)
}
