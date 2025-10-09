from __future__ import annotations
import pygame

# Layout utilities to align pygame surfaces and render texts

def pad_surface(surface: pygame.Surface,
                padding_size: int, padding_color: tuple | None = None,
                vertical_padding: bool = True, horizontal_padding: bool = True) -> pygame.Surface:
    """
    Add padding of given color and numbers of pixel around a Pygame surface.
    vertical_padding, horizontal_padding : bool - indicate if padding is desired from all sides
    """
    x,y = 0,0
    if vertical_padding:
        y+=padding_size
    if horizontal_padding:
        x+=padding_size
    result = pygame.Surface((surface.get_width()+2*x,surface.get_height()+2*y))
    if padding_color is not None:
        result.fill(padding_color)
    result.blit(surface,(x,y))
    return result

def align_surfaces(surfaces: pygame.Surface, orientation: str, alignment: str = "center",
                rescale_to_surface: pygame.Surface | None = None,
                spacing: int = 0, padding_size: int = 0, padding_color: tuple | None = None) -> pygame.Surface:
    """
    Align list of Pygame surfaces horizontally or vertically. Padding and spacing can be added.
    orientation : str
        "horizontal" or "vertical".
    alignment : str
        Alignment along the perpendicular axis
        ("center", "left", "right" for vertical; "center", "top", "bottom" for horizontal).
    rescale_to_surface : pygame.Surface | None
        If provided, rescale surfaces to match its height or width.
    """
    if surfaces == []:
        return pygame.Surface((0,0))

    if rescale_to_surface is not None:
        (w0,h0) = rescale_to_surface.get_size()
        if orientation == "horizontal":
            surfaces = [pygame.transform.scale_by(surface,h0/surface.get_height()) for surface in surfaces]
            h=h0
        elif orientation == "vertical":
            surfaces = [pygame.transform.scale_by(surface,w0/surface.get_width()) for surface in surfaces]
            w=w0
    else:
        if orientation == "horizontal":
            h = max(surface.get_height() for surface in surfaces)
        elif orientation == "vertical":
            w = max(surface.get_width() for surface in surfaces)

    if orientation == "horizontal":
        w = sum([surface.get_width() for surface in surfaces])  
        result = pygame.Surface((w+(len(surfaces)-1)*spacing,h), pygame.SRCALPHA)
        x,y = 0,0
        for surface in surfaces:
            if rescale_to_surface is not None or alignment == "top":
                y = 0
            elif alignment == "center":
                y=(h-surface.get_height())/2
            elif alignment == "bottom":
                y=h-surface.get_height()
            result.blit(surface,(x,y))
            x += surface.get_width() + spacing
    elif orientation == "vertical":
        h = sum([surface.get_height() for surface in surfaces])
        result = pygame.Surface((w,h+(len(surfaces)-1)*spacing), pygame.SRCALPHA)
        x,y = 0,0
        for surface in surfaces:
            if rescale_to_surface is not None or alignment == "left":
                x = 0
            elif alignment == "center":
                x=(w-surface.get_width())/2
            elif alignment == "right":
                x=w-surface.get_width()
            result.blit(surface,(x,y))
            y += surface.get_height() + spacing

    return pad_surface(result,padding_size, padding_color)

def render_line(line: list[str], font: pygame.Font, text_color: tuple, bg_color: tuple | None = None) -> pygame.Surface:
    """Render a line of text or a mix of text and surfaces as a single surface."""
    if isinstance(line, str):
        return font.render(line, False, text_color, bg_color)
    else:
        h = font.get_height()
        rendered_line_parts = []
        for part in line:
            if isinstance(part, str):
                rendered_line_parts.append(font.render(part, False, text_color, bg_color))
            else:
                rendered_line_parts.append(pygame.transform.scale_by(part,h/part.get_height()))
        return align_surfaces(rendered_line_parts, "horizontal", padding_color = bg_color)
    if rescale_to_size is not None:
        if orientation == "horizontal":
            h=rescale_to_size
            surfaces = [pygame.transform.scale_by(surface,h/surface.get_height()) for surface in surfaces]
        elif orientation == "vertical":
            w=rescale_to_size
            surfaces = [pygame.transform.scale_by(surface,w/surface.get_width()) for surface in surfaces]

class Text:
    """Render text with a given layout"""
    def __init__(self, lines: list[str], font: pygame.Font, text_color: tuple, bg_color: tuple | None = None):
        """For a list "lines" of strings (and surfaces) render its lines as surfaces
        that can be composed to a bigger surface with given alignment."""
        self.lines = lines
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.rendered_lines = [render_line(line, font, text_color, bg_color) for line in lines]
        self.max_line_length = max(line.get_width() for line in self.rendered_lines)
        self.title_length = self.rendered_lines[0].get_width()

    def render(self, alignment: str, line_distance: int,
        padding_size: int = 0, padding_color: tuple | None = None,
        center_title: bool = True, title_distance: int | None = None) -> pygame.Surface:
        """Composes rendered lines to a text with desired alignment 'left' or 'right', title formating, padding"""
        if padding_color is None:
            padding_color = self.bg_color
        if title_distance is None:
            title_distance = line_distance
        if len(self.lines) == 1:
            return pad_surface(self.rendered_lines[0], padding_size, padding_color)
        if center_title:
            rendered_text_body = align_surfaces(self.rendered_lines[1:], orientation="vertical",
                            alignment = alignment, spacing = line_distance, padding_size = 0, padding_color = self.bg_color)
            
            if self.rendered_lines[0].get_width() < self.max_line_length:
                rendered_text = align_surfaces([self.rendered_lines[0],rendered_text_body], orientation="vertical",
                            alignment = "center", spacing = title_distance, padding_size = 0, padding_color = self.bg_color)
            else:
                rendered_text = align_surfaces([self.rendered_lines[0],rendered_text_body], orientation="vertical",
                            alignment = alignment, spacing = title_distance, padding_size = 0, padding_color = self.bg_color)

        else:
            rendered_text = align_surfaces(self.rendered_lines, orientation="vertical",
                            alignment = alignment, spacing = line_distance, padding_size = 0, padding_color = self.bg_color)
        return pad_surface(rendered_text, padding_size, padding_color)