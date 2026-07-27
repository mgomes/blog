// walkgen renders a deterministic drunkard's-walk glyph field for each post,
// as transparent PNGs in light and dark ink. The walk is seeded from the
// post's filename slug, so a post's art never changes between runs.
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
	"strings"

	"golang.org/x/image/font"
	"golang.org/x/image/font/gofont/gomono"
	"golang.org/x/image/font/opentype"
	"golang.org/x/image/math/fixed"
)

const (
	gridW = 56
	gridH = 14
	steps = 1600

	fontSize = 28 // rendered at 2x for retina; displayed at half size
	lineH    = 30
)

// Density ramp from empty to peak. The top two levels get the accent ink.
var ramp = []rune(" ·:+*#@")

var (
	lightInk = color.NRGBA{R: 0x76, G: 0x76, B: 0x76, A: 0xff} // --fg-muted, light
	darkInk  = color.NRGBA{R: 0x8e, G: 0x92, B: 0x99, A: 0xff} // --fg-muted, dark
	accent   = color.NRGBA{R: 0x33, G: 0xa4, B: 0xd6, A: 0xff} // the sky flood
)

// lcg is a small deterministic PRNG (Numerical Recipes constants). Stability
// matters more than quality here: the same slug must draw the same walk on
// every machine forever.
type lcg struct{ s uint32 }

func (r *lcg) next() uint32 {
	r.s = r.s*1664525 + 1013904223
	return r.s >> 16
}

func walk(slug string) [gridH][gridW]int {
	h := fnv.New32a()
	h.Write([]byte(slug))
	rng := &lcg{s: h.Sum32()}

	var visits [gridH][gridW]int
	x, y := gridW/2, gridH/2
	visits[y][x]++

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

func levels(visits [gridH][gridW]int) [gridH][gridW]int {
	max := 0
	for y := range gridH {
		for x := range gridW {
			if visits[y][x] > max {
				max = visits[y][x]
			}
		}
	}
	var lv [gridH][gridW]int
	if max == 0 {
		return lv
	}
	top := len(ramp) - 1
	for y := range gridH {
		for x := range gridW {
			if v := visits[y][x]; v > 0 {
				l := (v*top + max - 1) / max
				if l < 1 {
					l = 1
				}
				lv[y][x] = l
			}
		}
	}
	return lv
}

func render(lv [gridH][gridW]int, ink color.NRGBA, face font.Face, advPx, ascent int) *image.NRGBA {
	img := image.NewNRGBA(image.Rect(0, 0, gridW*advPx, gridH*lineH))
	d := &font.Drawer{Dst: img, Face: face}
	for y := range gridH {
		for x := range gridW {
			l := lv[y][x]
			if l == 0 {
				continue
			}
			if l >= len(ramp)-2 {
				d.Src = image.NewUniform(accent)
			} else {
				d.Src = image.NewUniform(ink)
			}
			d.Dot = fixed.P(x*advPx, y*lineH+ascent)
			d.DrawString(string(ramp[l]))
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

	parsed, err := opentype.Parse(gomono.TTF)
	if err != nil {
		log.Fatal(err)
	}
	face, err := opentype.NewFace(parsed, &opentype.FaceOptions{Size: fontSize, DPI: 72, Hinting: font.HintingFull})
	if err != nil {
		log.Fatal(err)
	}
	adv, _ := face.GlyphAdvance('M')
	advPx := adv.Ceil()
	ascent := face.Metrics().Ascent.Ceil()

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
		lv := levels(walk(slug))
		light := render(lv, lightInk, face, advPx, ascent)
		dark := render(lv, darkInk, face, advPx, ascent)
		if err := writePNG(filepath.Join(*outDir, slug+"-light.png"), light); err != nil {
			log.Fatal(err)
		}
		if err := writePNG(filepath.Join(*outDir, slug+"-dark.png"), dark); err != nil {
			log.Fatal(err)
		}
		n++
	}
	fmt.Printf("generated %d walks in %s\n", n, *outDir)
}
