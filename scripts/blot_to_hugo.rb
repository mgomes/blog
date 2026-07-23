#!/usr/bin/env ruby
# One-off converter: Blot key-line posts -> Hugo YAML-frontmatter posts.
# Run from the repo root: ruby scripts/blot_to_hugo.rb
require "date"
require "yaml"
require "fileutils"

# Live URLs from mauriciogomes.com/sitemap.xml (Blot derives slugs from
# titles, not filenames, so these cannot be recomputed from the files).
SLUGS = {
  "abstraction-as-progress.md" => "/levels-of-abstraction-and-progress/",
  "blake2-for-ruby.md" => "/blake2b-for-ruby/",
  "cicada-3301.md" => "/cicada-3301/",
  "claude-obsidian-otis.md" => "/teaching-claude-code-my-obsidian-vault/",
  "cloudflare-pages-with-nanoc.md" => "/publish-to-cloudflare-pages-with-ruby-nanoc/",
  "computing-pi-in-go.md" => "/computing-π-in-go/",
  "cultivating_innovation.md" => "/innovation-isnt-produced-its-cultivated/",
  "dfs-vs-bfs.md" => "/maze-solving/",
  "introducing-stealth.md" => "/introducing-stealth/",
  "introducing-vibescript.md" => "/introducing-vibescript/",
  "kagi-mcp.md" => "/kagi-mcp-server/",
  "linkdump-apr2020.md" => "/link-dump-april-2020/",
  "linkdump-dec2019.md" => "/link-dump-december-2019/",
  "linkdump-mar2020.md" => "/link-dump-march-2020/",
  "linkdump-may2020.md" => "/link-dump-may-2020/",
  "novelty_distance.md" => "/novelty-distance/",
  "quantized-models.md" => "/selecting-a-llama-3-1-model-what-is-a-q4_k_s-anyway/",
  "rethinking-vibe-coding-interfaces.md" => "/rethinking-the-interface-for-vibe-coding/",
  "ruby_thread_current.md" => "/ruby-s-thread-current/",
  "theory-of-computational-irreducibility.md" => "/theory-of-computational-irreducibility/",
  "vibescript-0-26.md" => "/vibescript-v0-26-2/",
  "vibescript-native-showdown.md" => "/vibescript-in-the-native-showdown/",
  "vibescript-structured-concurrency.md" => "/structured-concurrency-lands-in-vibescript/",
  "wifi-on-xps-9300-linux.md" => "/wifi-connection-drops-on-dell-xps-13-9300-with-linux/",
}.freeze

abort "SLUGS has duplicate URLs" if SLUGS.values.uniq.size != SLUGS.size

HEADER_KEY = /\A(Date|Tags|Summary|Link):\s*(.*)\z/
YOUTUBE = %r{\Ahttps?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)\S*\s*\z}

def convert(src, dest, url:)
  lines = File.read(src).split("\n", -1)

  header = {}
  while (m = lines.first&.match(HEADER_KEY))
    header[m[1]] = m[2].strip
    lines.shift
  end
  lines.shift while lines.first&.empty?

  title_idx = lines.index { |l| l =~ /\A# (.+)\z/ }
  abort "#{src}: no H1 title" unless title_idx
  title = lines[title_idx].sub(/\A# /, "")
  preamble = lines[0...title_idx].reject(&:empty?)
  body = lines[(title_idx + 1)..]
  body.shift while body.first&.empty?

  in_math = false
  body = body.map do |line|
    if line.strip == "$$"
      in_math = !in_math
      line
    elsif in_math
      line.gsub(/\\\\/) { "\\" }
    elsif line.strip == "{{more}}"
      "<!--more-->"
    elsif line =~ YOUTUBE
      "{{< youtube #{$1} >}}"
    else
      line
    end
  end

  fm = { "title" => title }
  fm["date"] = Date.parse(header["Date"]).iso8601 if header["Date"]
  fm["tags"] = header["Tags"].split(",").map(&:strip) if header["Tags"]
  fm["description"] = header["Summary"] if header["Summary"]
  fm["url"] = url
  fm["math"] = true if body.any? { |l| l.include?("$$") }
  fm["updated"] = preamble.join(" ") unless preamble.empty?

  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, fm.to_yaml + "---\n\n" + body.join("\n").rstrip + "\n")
  puts "#{src} -> #{dest}"
end

Dir["posts/*.md"].sort.each do |src|
  slug = SLUGS[File.basename(src)] or abort "#{src}: not in SLUGS map"
  convert(src, "content/posts/#{File.basename(src)}", url: slug)
end

convert("pages/now.md", "content/now.md", url: "/now/")
