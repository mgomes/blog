Date: August 8, 2022
Tags: ruby
Summary: Use the Ruby Nanoc gem to publish Cloudflare Pages

# Publish to Cloudflare Pages with Ruby Nanoc

The Ruby [Nanoc gem](https://nanoc.app) is a fantastic gem for generating static websites. You get the benefits of partials, layouts, SCSS, helpers and other features without having to deploy an entire Ruby web framework. It all compiles down to plain ole' HTML and CSS.

For years, my Nanoc workflow looked like this:

1. Make changes locally
2. Run `nanoc` to generate the HTML and CSS
3. Upload the contents of `output/` to an S3 bucket using [Transmit](https://panic.com/transmit/)
4. Use Cloudflare to point a domain to the S3 bucket

This workflow served me pretty well, but it required a lot of manual steps. A few months ago I was able to replace steps 2 and 3 with a GitHub Action. The GitHub Action utilized a script for uploading content to an S3 bucket. It looked like this:

```yaml
name: Build and Upload to S3

on:
  push:
    branches:
      - master

jobs:
  build_and_upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@master
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.1.1
          bundler-cache: true

      - name: Build nanoc site
        run: bundle exec nanoc

      - uses: shallwefootball/s3-upload-action@master
        name: Upload to S3
        with:
          aws_key_id: ${{ secrets.AWS_KEY_ID }}
          aws_secret_access_key: ${{ secrets.AWS_SECRET_ACCESS_KEY}}
          aws_bucket: ${{ secrets.AWS_BUCKET }}
          source_dir: 'output'
          destination_dir: ''
```

The main downside to this approach is that each file is re-uploaded to S3 -- regardless of whether or not the file was modified.

## Cloudflare Pages

Yesterday Cloudflare [announced a generous free-tier](https://blog.cloudflare.com/big-ideas-on-pages/) for the Cloudflare Pages product. I was able to migrate a few static sites from S3 in just a few minutes. Cloudflare Pages connects to a GitHub or GitLab repository and automatically deploys your default branch to Cloudflare Pages. The flow is very similar to [Heroku GitHub Deploys](https://devcenter.heroku.com/articles/github-integration).

After migrating my static sites, I really wanted to replace my Nanoc + GitHub Actions + S3 workflow. At the time of this writing, the [build configuration documentation](https://developers.cloudflare.com/pages/platform/build-configuration/) didn't include an example for Nanoc. Fortunately, it was simple!

1. If your project already contains a `.ruby-version` file, Cloudflare will use that. Otherwise, you can set an environment variable called `RUBY_VERSION` to a version between `2.6.2` and `2.7.5` (these will likely change over time).
2. Ensure you project has a `Gemfile.lock`. This isn't mentioned anywhere, but Cloudflare will `bundle install` during the build.
3. Set the "Build command" to `nanoc`
4. Set the "Build output directory" to `/output` unless you've customized this in Nanoc.

That's it! As you make changes to your Nanoc site and merge those changes into your repository's default branch in GitHub or GitLab, Cloudflare Pages will build your site and deploy it to its global CDN.
