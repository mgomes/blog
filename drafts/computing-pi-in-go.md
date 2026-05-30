Date: May 30, 2026
Tags: go, projects
Summary: Computing digits of π in Go, and seeing how fast I could make it.

# Computing π in Go

Every so often I end up writing another program to compute the digits of π. I have no real need for it. It has never once come up in my actual work. But it is a tidy, self-contained problem with a clear right answer, and it makes a good excuse to get a feel for a language or a library.

I have done it before in Ruby and in Crystal. The Ruby version leans on Ramanujan's series and `BigDecimal`. The Crystal version uses the Chudnovsky formula with binary splitting. I also have a small pile of throwaway versions that various LLMs generated for me, using everything from the Bailey-Borwein-Plouffe formula to Bellard's. This time I reached for Go.

{{more}}

## The algorithm

Chudnovsky is the usual choice. It converges quickly, adding roughly 14 digits of π per term:

$$\frac{1}{\pi} = 12 \sum_{k=0}^{\infty} \frac{(-1)^k (6k)!\,(545140134k + 13591409)}{(3k)!\,(k!)^3\,640320^{3k + 3/2}}$$

Evaluated term by term the sum is $$O(n^2)$$, since the factorials keep growing. The standard fix is binary splitting. Instead of computing each term on its own, you write the partial sum over a range as a single fraction, then combine the left and right halves of the range recursively. That turns the whole thing into a balanced tree of large integer multiplications, which is a much nicer shape to work with.

Go has arbitrary precision integers in `math/big`, so a first version was easy. Then I wanted to see how fast I could push it.

## Going faster

The first thing I learned is that `math/big` tops out at Karatsuba multiplication, which is about $$O(n^{1.585})$$. There is no FFT-based multiply in the standard library. At the operand sizes you reach computing a million digits, that is the wall.

There is a pure-Go library, [bigfft](https://github.com/remyoudompheng/bigfft), that implements Schönhage-Strassen multiplication. Swapping it in for the large multiplies moves you toward $$O(n \log n)$$.

My first benchmark said bigfft was slower at every size, which made no sense. The catch is that FFT carries real setup cost, building up its transform tables, and I was not running enough iterations to amortize it. Once I measured properly the picture flipped. At a million-digit operand bigfft was around 5x faster, and the gap only widens past that.

The part I enjoyed was watching the bottleneck move. Once the multiplications were cheap, the final division was the slow step. Go's division is Karatsuba-bound too, so I wrote a Newton reciprocal that does the division with FFT multiplies instead. Then the square root became the slowest step, since the formula needs $$\sqrt{10005}$$, so that got the same treatment with a Newton inverse square root. Every fix just uncovered the next thing in line, until the whole pipeline was running on FFT.

One other thing was worth catching. For a while the program would "compute" the 100,000th digit in 30 milliseconds and then take three and a half seconds to actually finish. The culprit was the bit that prints a few digits of context around the answer. It was asking `big.Float` to format the entire number to text, which does a full base conversion. The time you print is not always the time you compute.

## Where it landed

Total wall time to compute a digit on a 10-core machine (Apple Silicon M1 Max), from the first straightforward version to the FFT one:

| digit      | before | after  |
| ---------- | ------ | ------ |
| 100,000    | 3.5 s  | 33 ms  |
| 1,000,000  | 1.3 s  | 0.48 s |
| 10,000,000 | 53 s   | 9 s    |

None of this is useful to me. But computing π is a reliable way to find a language's sharp edges, and Go's turned out to be the missing FFT multiply in its standard library. The code is [on GitHub](https://github.com/mgomes/chudnovsky) if you want to poke at it.
