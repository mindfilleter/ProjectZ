import pygame

from projectz.core import entity


class RenderComponent(entity.Component):
    def __init__(
        self,
        size: tuple[int, int],
        color: pygame.Color,
        text: str,
        border_radius: int = 0,
        font_size: int = 24,
        text_color: pygame.Color = pygame.Color("white"),
    ) -> None:
        super().__init__()
        self.shadow_offset = 3
        self.original_size = size
        self.color = color
        self.text = text
        self.border_radius = border_radius
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color

        # The image needs to be bigger to accommodate the shadow
        image_size = (size[0] + self.shadow_offset, size[1] + self.shadow_offset)
        self.image = pygame.Surface(image_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.redraw()

    def update(self, dt: int) -> None:
        pass

    def handle_event(self, pygame_event: pygame.event.Event) -> bool:
        return False

    def redraw(self) -> None:
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        face_rect = pygame.Rect((0, 0), self.original_size)
        shadow_rect = face_rect.move(self.shadow_offset, self.shadow_offset)

        # 1. Draw shadow
        shadow_color = pygame.Color(0, 0, 0, 100)
        pygame.draw.rect(self.image, shadow_color, shadow_rect, border_radius=self.border_radius)

        # 2. Draw gradient for the face
        top_color = self.color.lerp(pygame.Color("white"), 0.4)
        bottom_color = self.color.lerp(pygame.Color("black"), 0.2)

        gradient_surface = pygame.Surface(face_rect.size, pygame.SRCALPHA)
        for y in range(face_rect.height):
            t = y / face_rect.height
            lerped_color = top_color.lerp(bottom_color, t)
            pygame.draw.line(gradient_surface, lerped_color, (0, y), (face_rect.width, y))

        mask_surface = pygame.Surface(face_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            mask_surface,
            pygame.Color("white"),
            mask_surface.get_rect(),
            border_radius=self.border_radius,
        )

        gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.image.blit(gradient_surface, face_rect.topleft)

        # 3. Draw border
        border_color = pygame.Color(0, 0, 0, 180)
        pygame.draw.rect(
            self.image, border_color, face_rect, width=1, border_radius=self.border_radius
        )

        # 4. Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=face_rect.center)
            self.image.blit(text_surface, text_rect)
