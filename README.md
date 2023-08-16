# Notion2Hugo

Export content written in Notion to markdown, compatible for [Hugo](https://gohugo.io/) blog.

You can use Notion as a CMS in order to author, edit, and manage all your content while leverage the power of Hugo in order to serve the content statically on your blog site. This lets you leverage the best of both worlds - powerful and expressive UX of Notion for authoring along with speed and pre-built feature rich themes for personal blog site.

The package ships with a script in order to export content from Notion in a compatible format.

```shell
$ publish_notion_to_hugo [-h] config_path
```

## Getting Started

Follow the steps below to get started:
1. Follow the Notion developer guide in order to [setup an Access Token and an Integration](https://developers.notion.com/docs/authorization) with at least "Read" access to the relevant database.
2. Expose the access token and the database ID as environment variables in your shell.
   ```
   export NOTION_TOKEN='<your-access-token-here>'
   export NOTION_DATABASE_ID='<database-id-with-read-integration-setup>'
   ```
3. Clone the `src/notion2hugo/config.sample.toml` file as `config.toml` and add in your custom settings. You can leverage the properties in your Notion database in order to determine the name of the published post.
4. Run the script mentioned above and profit!
   ```bash
   $ publish_notion_to_hugo /path/to/config.toml
   ```

### Note about output structure

Currently, the output markdown generated has the following directory structure:
- {parent_dir}/ (_provided in the config, cleared at the start of execution_)
  - {post1_name}/ (_provided in the config or defaults to the "Title" property auto populated for all posts_)
    - images/ (_contains all the image assets used in the post_)
    - index.md (_contains the exported post markdown content with an appropriately formatter front matter_)
  - {post2_name}/
    - images/
    - index.md
  - ...

### Note about `index.md` front matter

We export all the properties specified in the Notion database for the page to the front matter in the format shown below:
```
---
prop1: prop1_value
prop2: prop2_value
...
Title: 'Post title"
---
```

This is intended to mimic the front matter [format as shown here](https://gohugo.io/getting-started/quick-start/#add-content). The full list of supported front matter variables is provided here - [front matter variables](https://gohugo.io/content-management/front-matter/#front-matter-variables).

The Notion database can be setup in order to have properties as supported by Hugo in order to easily export them and make the best use of the options available. For ex, you could have a property as:
- `"Draft"` with a value of `"false"` or `"true"` and Hugo will correctly handle them as a draft post or a published post.-
- `Date` property can be used to specify the post publish date.
- `Tags`, `Series`...
- On the flip side, if you'd like to have other arbitrary properties in your Notion database, you should prepend them with a `#` (eg, `# Arbitrary Prop`), so that they don't interfere with Hugo front matter format and don't result in an error.

## Configuration

Here is the [`config.sample.toml`](https://github.com/chintak/notion2hugo/blob/master/src/notion2hugo/config.sample.toml):

```toml
#
# Copy this file to config.toml and update the field below
#

[provider_config]
## override the id here or defaults to NOTION_DATABASE_ID env
# database_id = "<notion_database_id>"
## specify filter here, refer to Notion API Dev resources for format
# filter = {property = "# Status", status = {equals = "Outline"}}
# filter = {property = "# Status", status = {does_not_equal = "Not Started"}}

[formatter_config]

[exporter_config]
parent_dir = "/tmp/notion2hugo_output_dir"
## specify page prop from Notion here or
## remove it in order use page id as dir
post_name_property_key = "Title" # 'Title' prop is added by default.

[runner_config]
exporter_config_cls = "notion2hugo.exporter.MarkdownExporterConfig"
formatter_config_cls = "notion2hugo.formatter.HugoFormatterConfig"
provider_config_cls = "notion2hugo.provider.NotionProviderConfig"
```

## Supported Features

Exporting markdown for the following Notion features is supported:
- [X] Heading 1/2/3/Paragraphs
- [X] Text annotations - bold, italics, underline, etc.
- [X] Table (with markdown in cells)
- [X] Images (with captions)
- [X] Code (inline and block)
- [X] [Mermaid diagrams](https://mermaid.js.org/)
- [X] Blockquote
- [X] Math equations (both inline and block)
- [X] Text Highlight

## Roadmap for future developement

Currently, the following Notion features are not supported for export and will be supported in future versions:

- [X] Checklist or TODOs
- [ ] Callouts
- [ ] Cross referencing pages in the database, that is, we'd like to update the URL appropriately to refer to the published post on the blog rather than to the notion page.
- [ ] Gist, twitter or other embeds.

## Contributions

Contributions are more than welcome! Please feel free to open an issue or a pull request for any bugs/feature request or any other improvements. Cheers!