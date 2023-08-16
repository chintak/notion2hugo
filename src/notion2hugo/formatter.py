from dataclasses import dataclass

from notion2hugo.base import (
    BaseFormatter,
    BaseFormatterConfig,
    Blob,
    BlobType,
    ContentWithAnnotation,
    PageContent,
    register_handler,
)


@dataclass(frozen=True)
class HugoFormatterConfig(BaseFormatterConfig):
    pass


@register_handler(HugoFormatterConfig)
class HugoFormatter(BaseFormatter):
    def __init__(self, config: HugoFormatterConfig):
        super(HugoFormatter, self).__init__(config)
        self.config: HugoFormatterConfig = config

    async def async_process(self, content: PageContent) -> PageContent:
        # process properties and format header
        header_props = [f"# ID: {content.id}"]
        header_props.extend(
            f"{k}: {v}" for k, v in sorted(content.properties.items()) if v
        )
        header_blob = Blob(
            id="header",
            rich_text=[
                ContentWithAnnotation(plain_text="---\n"),
                ContentWithAnnotation(plain_text="\n".join(header_props)),
                ContentWithAnnotation(plain_text="\n---\n"),
            ],
            type=BlobType.PARAGRAPH,
            children=None,
            file=None,
            language=None,
            table_width=None,
            table_cells=None,
            is_checked=None,
        )

        return PageContent(
            blobs=content.blobs,
            id=content.id,
            properties=content.properties,
            footer=None,
            header=header_blob,
        )
