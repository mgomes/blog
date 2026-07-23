# Serve locally with drafts (-D) and future-dated posts (-F) visible
default: serve

serve:
    hugo server -D -F

# Production build into public/
build:
    hugo --minify --cleanDestinationDir

# Scaffold a draft: just draft my-post-slug
draft name:
    hugo new posts/{{name}}.md
