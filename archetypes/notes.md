---
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
date: '{{ time.Now.Format "2006-01-02" }}'
# film, tv, book, music, or note (a short post with no object)
medium: note
# Director, author, or artist. Year is optional.
creator: ''
year: ''
# 1 to 5 squares, or leave empty for no rating
rating:
# One to three names from static/glyphs.svg (see tools/glyphs/draw.py)
glyphs: []
# lime, ink, red, cobalt, tangerine, paper, or pink. Picked from the title if empty.
color: ''
tags: []
draft: true
---
