"""
Sphinx directive for HTML Hero Components.
"""
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from .utils import generate_template


class HeroBox(Directive):
    has_content = True
    option_spec = {
        "title": directives.unchanged_required,
        "class": directives.path,
        "text": directives.unchanged_required,
        "image": directives.path,
        "button_icon": directives.path,
        "button_url": directives.path,
        "button_text": directives.path,
        "search_box": directives.flag,
    }

    def run(self):
        class_name = "hero"
        container_class_name = self.options.get("class", "")

        image = self.options.get("image")
        image = (
            generate_template(
                """
                <img src="{image}" />
                """,
                image=image,
            )
            if image
            else ""
        )

        button_icon = self.options.get("button_icon")
        button_url = self.options.get("button_url")
        button_text = self.options.get("button_text")
        button = (
            generate_template(
                """
                <a href="{button_url}">
                <button class="{class_name}__button button">
                <i class="icon {button_icon}" aria-hidden="true"></i>
                {button_text}
                </button>
                </a>
                """,
                button_icon=button_icon,
                button_url=button_url,
                button_text=button_text,
                class_name=class_name,
            )
            if button_text
            else ""
        )

        has_search_box = "search_box" in self.options
        search_box = (
            generate_template(
                """
                <div class="{class_name}__search-box search-box search-box--hero">
                <ci-search></ci-search>
                </div>
                """,
                class_name=class_name,
            )
            if has_search_box
            else ""
        )

        html_tag_open = generate_template(
            """
            <div class="{class_name} {container_class_name}">
                <div class="{class_name}-wrapper">
                    <div class="{class_name}__img">
                    {image}
                    </div>
                    <div class="{class_name}-header">
                        <h1 class="{class_name}__title">{title}</h1>
                        <div class="{class_name}__text">
            """,
            title=self.options.get("title", ""),
            image=image,
            class_name=class_name,
            container_class_name=container_class_name,
        )
        html_tag_close = generate_template(
            """</div>{button}{search_box}</div></div></div>""",
            button=button,
            search_box=search_box,
        )
        description_node = nodes.container()
        if self.state:
            self.state.nested_parse(self.content, 0, description_node)

        return [
            nodes.raw(text=html_tag_open, format="html"),
            description_node,
            nodes.raw(text=html_tag_close, format="html"),
        ]


def setup(app):
    app.add_directive("hero-box", HeroBox)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
