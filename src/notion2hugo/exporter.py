import os
import re
import shutil
from dataclasses import dataclass
from typing import List, Optional

from notion2hugo.base import (
    BaseExporter,
    BaseExporterConfig,
    Blob,
    BlobType,
    ContentWithAnnotation,
    PageContent,
    register_handler,
)


def sanitize_path(name: str) -> str:
    pattern = re.compile(r"[^a-zA-Z0-9-_\.]")
    return pattern.sub("", name)


class MarkdownStyler:
    INC_INDENT: int = 4

    @classmethod
    def _style_content_with_annotation(cls, texts: List[ContentWithAnnotation]) -> str:
        ts = []
        for text in texts:
            t = text.plain_text
            if not t:
                return ""
            if text.bold:
                t = f"**{t}**"
            if text.italic:
                t = f"_{t}_"
            if text.strikethrough:
                t = f"~~{t}~~"
            if text.underline:
                t = f"<ins>{t}</ins>"
            if text.code:
                t = f"`{t}`"
            if text.color:
                pass
            if text.href:
                t = f"[{t}]({text.href})"
            if text.is_equation:
                t = f"$ {t} $"
            if text.highlight:
                t = f"<mark>{t}</mark>"
            ts.append(t)
        return "".join(ts)

    @classmethod
    def divider(cls, blob: Blob, indent: int) -> str:
        return "\n---\n"

    @classmethod
    def heading_1(cls, blob: Blob, indent: int) -> str:
        return f"# {cls.paragraph(blob, indent)}"

    @classmethod
    def heading_2(cls, blob: Blob, indent: int) -> str:
        return f"## {cls.paragraph(blob, indent)}"

    @classmethod
    def heading_3(cls, blob: Blob, indent: int) -> str:
        return f"### {cls.paragraph(blob, indent)}"

    @classmethod
    def equation(cls, blob: Blob, indent: int) -> str:
        return f"$$\n{cls.paragraph(blob, indent)}\n$$"

    @classmethod
    def code(cls, blob: Blob, indent: int) -> str:
        return "\n".join([f"```{blob.language}", cls.paragraph(blob, indent), "```"])

    @classmethod
    def _list_item(cls, blob: Blob, list_ch: str, indent: int) -> str:
        whitespace: str = " " * indent
        texts = [
            f"{whitespace}{list_ch} {cls._style_content_with_annotation(blob.rich_text)}"
        ]
        if blob.children:
            for child_blob in blob.children:
                texts.append(cls.process(child_blob, indent + cls.INC_INDENT))
        return "\n".join(texts)

    @classmethod
    def bulleted_list_item(cls, blob: Blob, indent: int) -> str:
        return cls._list_item(blob, list_ch="-", indent=indent)

    @classmethod
    def numbered_list_item(cls, blob: Blob, indent: int) -> str:
        return cls._list_item(blob, list_ch="1.", indent=indent)

    @classmethod
    def to_do(cls, blob: Blob, indent: int) -> str:
        return cls._list_item(
            blob, list_ch=f"- [{'X' if blob.is_checked else ' '}]", indent=indent
        )

    @classmethod
    def quote(cls, blob: Blob, indent: int) -> str:
        texts = [f"> {cls._style_content_with_annotation(blob.rich_text)}"]
        if blob.children:
            for child_blob in blob.children:
                texts.append(
                    f"> {cls._style_content_with_annotation(child_blob.rich_text)}"
                )
        return "\n>\n".join(texts)

    @classmethod
    def table(cls, blob: Blob, indent: int) -> str:
        assert blob.table_width, f"table_width expected for TABLE blob {blob}"
        rows = []
        if blob.children:
            rows = [cls.process(child_blob, indent) for child_blob in blob.children]
            if len(rows) >= 1:
                rows.insert(1, "\n|" + "---|" * blob.table_width)
        return "".join(rows)

    @classmethod
    def table_row(cls, blob: Blob, indent: int) -> str:
        assert blob.table_cells, f"table_cells expected for TABLE_ROW blob {blob}"
        return (
            "| "
            + " | ".join(
                cls._style_content_with_annotation(cell) for cell in blob.table_cells
            )
            + " |"
        )

    @classmethod
    def image(cls, blob: Blob, indent: int) -> str:
        assert blob.file and os.path.exists(
            blob.file
        ), f"file expected for IMAGE blob {blob}"
        # prepare caption
        caption = cls._style_content_with_annotation(blob.rich_text)
        relative_path = os.path.join(
            MarkdownExporter.POST_IMAGES_DIR, os.path.basename(blob.file)
        )
        return (
            f'{{{{< figure src="{relative_path}" '
            f'caption="{caption}" align="center" >}}}}'
        )

    @classmethod
    def paragraph(cls, blob: Blob, indent: int) -> str:
        texts = [cls._style_content_with_annotation(blob.rich_text)]
        if blob.children:
            for child_blob in blob.children:
                texts.append(cls.process(child_blob, indent + cls.INC_INDENT))
        return "\n".join(texts)

    @classmethod
    def process(cls, blob: Optional[Blob], indent: int = 0) -> str:
        if not blob:
            return ""
        if not hasattr(cls, blob.type.value):
            raise ValueError(
                f"{cls.__qualname__} does not support blob type = {blob.type.value}.\n"
                f"Blob: {blob}"
            )
        return "\n" + getattr(cls, blob.type.value)(blob, indent)


@dataclass(frozen=True)
class MarkdownExporterConfig(BaseExporterConfig):
    parent_dir: str
    # use one of the page properties to determine post dir/file name
    # # if not specified, we default to using "id" as name
    post_name_property_key: Optional[str] = None


@register_handler(MarkdownExporterConfig)
class MarkdownExporter(BaseExporter):
    POST_FILE_NAME: str = "index.md"
    POST_IMAGES_DIR: str = "images/"

    def __init__(self, config: MarkdownExporterConfig):
        super(MarkdownExporter, self).__init__(config)
        self.config: MarkdownExporterConfig = config
        self.logger.info(f"Clean up parent dir: {self.config.parent_dir}")
        self.cleanup_parent_dir(self.config.parent_dir)

    def cleanup_parent_dir(self, parent_dir: str) -> None:
        if os.path.exists(parent_dir):
            shutil.rmtree(parent_dir)

    def make_output_dirs(self, parent_dir: str, *args: str) -> None:
        os.makedirs(os.path.join(parent_dir, *args), exist_ok=True)

    async def async_process(self, content: PageContent) -> None:
        # prepare post output dir structure
        # parent_dir/
        #     post_1/
        #         images/
        #         index.md
        assert not self.config.post_name_property_key or content.properties.get(
            self.config.post_name_property_key
        ), (
            f"{self.config.post_name_property_key} not a valid "
            "property [{content.properties.keys()}]"
        )
        post_dir_name = (
            content.properties[self.config.post_name_property_key]
            if self.config.post_name_property_key
            else content.id
        )
        assert isinstance(post_dir_name, str), f"{post_dir_name} expected to be str"
        post_dir_name = sanitize_path(post_dir_name)
        post_images_dir = os.path.join(
            self.config.parent_dir, post_dir_name, self.POST_IMAGES_DIR
        )
        self.logger.debug(f"Creating output dir structure: {post_images_dir}")
        self.make_output_dirs(post_images_dir)
        post_full_path = os.path.join(
            self.config.parent_dir, post_dir_name, self.POST_FILE_NAME
        )

        # prepare post content and write it out
        self.logger.debug("Processing blobs to prepare markdown content")
        texts = []
        texts.append(MarkdownStyler.process(content.header))
        for blob in content.blobs:
            if blob.type == BlobType.IMAGE:
                # copy image to local dir
                assert blob.file and os.path.exists(
                    blob.file
                ), f"file expected for IMAGE blob {blob}"
                new_img_path = shutil.move(blob.file, post_images_dir)
                blob = Blob(
                    id=blob.id,
                    rich_text=blob.rich_text,
                    type=blob.type,
                    children=blob.children,
                    file=new_img_path,
                    language=blob.language,
                    table_width=blob.table_width,
                    table_cells=blob.table_cells,
                    is_checked=blob.is_checked,
                )
            texts.append(MarkdownStyler.process(blob))
        texts.append(MarkdownStyler.process(content.footer))

        self.logger.info(f"Export post id={content.id} to path='{post_full_path}'")
        with open(post_full_path, "w") as fp:
            fp.write("\n".join(texts).strip())
