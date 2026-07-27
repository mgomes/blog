// walkgen renders a deterministic drunkard's-walk glyph field for each post,
// as transparent PNGs in light and dark ink. The walk is seeded from the
// post's filename slug, so a post's art never changes between runs.
//
// The look is a full-bleed fabric: a long walk's visit counts are blurred
// into smooth density, then every cell gets a glyph from a ramp, so valleys
// read as faint dots, the mid field as a sea of tildes, and the walk's// favorite places as heavy waves merging into solid islands.
package main

import (
	"flag"
	"fmt"
	"hash/fnv"
	"image"
	"image/color"
	"image/png"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"golang.org/x/image/font"
	"golang.org/x/image/font/gofont/gomono"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/math/fixed"
)

const (
	gridW = 54
	gridH = 27
	steps = 45000

	// Rendered at 2x and displayed at half size. The display width works
	// out to gridW * advance / 2, which sits just inside the 648px column
	// so the PNG is never resampled.
	cellPx = 24
)

var (
	lightInk = color.NRGBA{R: 0x76, G: 0x76, B: 0x76} // --fg-muted, light
	darkInk  = color.NRGBA{R: 0x8e, G: 0x92, B: 0x99} // --fg-muted, dark
)

// The density ramp. Alpha and glyph size carry the tonal range within a
// single ink so the same PNG works over the paper and dark backgrounds.
// Small and large variants of each wave glyph are what give the field its
// in-between tones; a single size per glyph read as three flat bands.
type level struct {
	glyph rune
	alpha uint8
	size  float64
}

var ramp = []level{
	{'·', 90, 24},
	{'~', 140, 24},
	{'~', 190, 34},
	{'≈', 215, 24},
	{'≈', 245, 34},
	{'█', 255, 24},
	{'█', 255, 34},
}

// Cumulative area cuts on the shaded value; one fewer than ramp entries.
// Weighted so mist and small ripples carry most of the field and islands
// stay rare.
var cuts = []float64{0.30, 0.55, 0.72, 0.85, 0.94, 0.985}

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
			v += (float64(rng.next()%1000)/1000 - 0.5) * 0.09
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

type cellFace struct {
	face font.Face
	xoff int
}

func render(lv [][]int, ink color.NRGBA, faces map[float64]cellFace, baseline int) *image.NRGBA {
	img := image.NewNRGBA(image.Rect(0, 0, gridW*cellPx, gridH*cellPx))
	d := &font.Drawer{Dst: img}
	for y := range gridH {
		for x := range gridW {
			l := ramp[lv[y][x]]
			cf := faces[l.size]
			c := ink
			c.A = l.alpha
			d.Face = cf.face
			d.Src = image.NewUniform(c)
			d.Dot = fixed.P(x*cellPx+cf.xoff, y*cellPx+baseline)
			d.DrawString(string(l.glyph))
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

func loadFont(path string) ([]byte, string) {
	if path != "" {
		if b, err := os.ReadFile(path); err == nil {
			return b, path
		}
		log.Printf("cannot read %s; falling back to Go Mono", path)
	}
	return gomono.TTF, "Go Mono (embedded)"
}

func main() {
	home, _ := os.UserHomeDir()
	contentDir := flag.String("content", "content/posts", "directory of post markdown files")
	outDir := flag.String("out", "static/_Images/walks", "output directory for PNGs")
	fontPath := flag.String("font", filepath.Join(home, "Library/Fonts/MonoLisaCodeUpright.ttf"), "TTF/OTF to rasterize with")
	rampFlag := flag.String("ramp", "", "glyphs for the density ramp, faint to peak (default ··~~≈≈██ sizes vary)")
	flag.Parse()

	if *rampFlag != "" {
		runes := []rune(*rampFlag)
		if len(runes) != len(ramp) {
			log.Fatalf("-ramp needs exactly %d glyphs, got %d", len(ramp), len(runes))
		}
		for i, r := range runes {
			ramp[i].glyph = r
		}
	}

	ttf, fontName := loadFont(*fontPath)
	parsed, err := opentype.Parse(ttf)
	if err != nil {
		log.Fatal(err)
	}
	faces := map[float64]cellFace{}
	for i, l := range ramp {
		if _, ok := faces[l.size]; ok {
			continue
		}
		face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: l.size, DPI: 72, Hinting: font.HintingFull})
		if err != nil {
			log.Fatal(err)
		}
		if _, ok := face.GlyphAdvance(l.glyph); !ok {
			log.Fatalf("%s has no glyph for %q (ramp level %d)", fontName, l.glyph, i)
		}
		adv, _ := face.GlyphAdvance('M')
		// Center each glyph horizontally in its fixed cell.
		faces[l.size] = cellFace{face: face, xoff: (cellPx - adv.Ceil()) / 2}
	}
	baseline := cellPx - cellPx/6

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
		light := render(lv, lightInk, faces, baseline)
		dark := render(lv, darkInk, faces, baseline)
		if err := writePNG(filepath.Join(*outDir, slug+"-light.png"), light); err != nil {
			log.Fatal(err)
		}
		if err := writePNG(filepath.Join(*outDir, slug+"-dark.png"), dark); err != nil {
			log.Fatal(err)
		}
		n++
	}
	fmt.Printf("generated %d walks in %s with %s\n", n, *outDir, fontName)
}
