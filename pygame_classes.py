import pygame

pygame.init()
screen_info = pygame.display.Info()
sw = screen_info.current_w  # Width of the screen
sh = screen_info.current_h  # Height of the screen
print(sw, sh)
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (211, 211, 211)
BUTTON_NORMAL = (150, 150, 150)
BUTTON_HOVER = (200, 200, 200)
BUTTON_CLICKED = (100, 100, 100)
BUTTON_DISABLED = (100, 100, 100)  # Color for disabled button

WIDTH, HEIGHT = 800, 600
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 10
KNOB_RADIUS = 15
BACKGROUND_COLOR = (255, 255, 255)
SLIDER_COLOR = (200, 200, 200)
KNOB_COLOR = (0, 128, 255)
TEXT_COLOR = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 42)
chips_font = pygame.font.Font(None, 20)


def get_screen_info():
    global sw
    global sh
    return sw, sh


class Button:
    def __init__(self, width, height, text, x=None, y=None):
        if x is None and y is None:
            self.rect = pygame.Rect(0, 0, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.active = False  # If the button is clicked
        self.hover = False  # If the mouse is hovering over the button
        self.click_time = None
        self.clickable = True  # Default to clickable

    def draw(self, screen, x=None, y=None):
        # Change button color based on hover, click or disabled state
        if self.active:
            button_color = BUTTON_CLICKED
        elif self.hover:
            button_color = BUTTON_HOVER
        elif not self.clickable:
            button_color = BUTTON_DISABLED
        else:
            button_color = BUTTON_NORMAL
        if x is not None and y is not None:
            self.rect.x = x
            self.rect.y = y
            pygame.draw.rect(screen, button_color, self.rect)  # Draw the button
        else:
            pygame.draw.rect(screen, button_color, self.rect)  # Draw the button
        # Draw text
        text_surface = font.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.clickable:
            self.active = True
            self.click_time = pygame.time.get_ticks()
            return True
        return False

    def check_hover(self, pos):
        # Check if the mouse is hovering over the button
        if self.rect.collidepoint(pos):
            self.hover = True
        else:
            self.hover = False

    def reset_after_click(self):
        # Reset the button state after 500ms (0.5 seconds)
        if self.active and pygame.time.get_ticks() - self.click_time > 400:
            self.active = False

    def disable(self):
        self.clickable = False  # Disable the button

    def enable(self):
        self.clickable = True  # Enable the button

    def update_text(self, text):
        self.text = text


class TextInput:
    def __init__(self, x, y, width, height, max_characters=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_characters = max_characters
        self.text = ''  # The text typed into the input field
        self.active = False  # If the input field is focused
        self.border_color = (150, 150, 150)  # Default border color
        self.text_color = BLACK

    def draw(self, screen):
        # Change border color if the field is active
        border_color = (0, 0, 0) if self.active else self.border_color

        # Draw the input field (background and border)
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)

        # Draw the text inside the input field
        text_surface = large_font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.x + 10, self.y + 5))

    def handle_event(self, event, only_digit=False):
        """Handle user input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the input field was clicked
            if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(event.pos):
                self.active = True  # Focus the input field
            else:
                self.active = False  # Lose focus if clicked outside

        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    # Remove the last character on backspace
                    self.text = self.text[:-1]
                elif len(self.text) < self.max_characters:
                    if only_digit:
                        # Only allow digits (0-9)
                        if event.key in range(pygame.K_0, pygame.K_9 + 1):
                            self.text += event.unicode
                    else:
                        # Allow all characters
                        self.text += event.unicode

    def get_text(self):
        """Get the current text"""
        return self.text

    def set_text(self, t):
        self.text = t


class CardImages:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = sw * 0.08
        self.height = self.width * 19/14
        self.cards = []
        for i in range(5):
            image = 'backs/back04.svg'
            self.cards.append(image)

    def update_img(self, index, img):
        self.cards[index] = img

    def reset(self):
        for i in range(5):
            image = 'backs/back04.svg'
            self.cards[i] = image

    def draw(self, screen):
        i = 0
        for image in self.cards:
            image = pygame.image.load(image)
            scaled_image = pygame.transform.scale(image, (self.width, self.height))
            screen.blit(scaled_image, (self.x + i * (self.width + sw * 0.02), self.y))
            i += 1


class TextDisplay:
    def __init__(self, font_size=36, color=(0, 0, 0), text=''):
        self.font_size = font_size
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, self.font_size)
        self.text_surface = self.font.render(self.text, True, self.color)

    def update_text(self, new_text):
        """Update the text displayed"""
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen, x, y):
        screen.blit(self.text_surface, (x, y))

    def get_surface(self):
        return self.text_surface


class ChipsDisplay:
    def __init__(self, width, height, text, image='images/golden-apple.png'):
        # Load and scale the image
        self.width = width
        self.height = height
        loaded_image = pygame.image.load(image)
        image_size = (sw / 25, sw / 25)
        self.image = pygame.transform.scale(loaded_image, image_size)
        self.text = TextDisplay(36, (0, 0, 0), text)
        self.padding = 5

        # Render the text
        self.text_surface = self.text.get_surface()

        # Calculate the combined width and height (using the maximum height)
        self.content_width = self.image.get_width() + self.text_surface.get_width() + self.padding
        self.content_height = max(self.image.get_height(), self.text_surface.get_height())

        # Create a surface to combine the image and text
        self.combined_surface = pygame.Surface((self.width, self.height))
        self.combined_surface.fill((46, 77, 62))

        # Blit the image onto the combined surface
        self.image_rect = self.image.get_rect(
            topleft=((self.width - self.content_width)/2, (self.height - self.content_height)/2)
        )
        self.combined_surface.blit(self.image, self.image_rect)

        # Blit the text onto the combined surface (next to the image)
        self.text_rect = self.text_surface.get_rect(
            topleft=((self.width - self.content_width)/2 + self.image.get_width() + self.padding,
                     (self.height - self.content_height)/2)
        )
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def update_chips(self, chips):
        # Update the text with the new chip count
        # Re-render the text surface
        self.text.update_text(str(chips))
        self.text_surface = self.text.get_surface()

        # Update the width and height based on the new text
        self.content_width = self.image.get_width() + self.text_surface.get_width() + self.padding
        self.content_height = max(self.image.get_height(), self.text_surface.get_height())

        # Create a new surface to combine the image and updated text
        self.combined_surface = pygame.Surface((self.width, self.height))
        self.combined_surface.fill((46, 77, 62))

        # Blit the image onto the combined surface
        self.image_rect = self.image.get_rect(
            topleft=((self.width - self.content_width)/2, (self.height - self.image.get_height())/2)
        )
        self.combined_surface.blit(self.image, self.image_rect)

        # Blit the text onto the combined surface (next to the image)
        self.text_rect = self.text_surface.get_rect(
            topleft=((self.width - self.content_width)/2 + self.image.get_width() + self.padding,
                     (self.height - self.text.get_surface().get_height())/2)
        )
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def draw(self, screen, x, y):
        # Position the combined element inside the main rect
        screen.blit(self.combined_surface, (x, y))

    def get_surface(self):
        return self.combined_surface


class PlayerDisplay:
    def __init__(self, text, chips, padding=5):
        self.padding = padding
        self.chips = chips
        self.text = text
        self.image = pygame.image.load('backs/back04.svg')
        self.image_width = sw * 0.06
        self.image_height = self.image_width * 219/185
        self.image = pygame.transform.scale(self.image, (self.image_width, self.image_height))

        self.text_surface = font.render(self.text, True, WHITE)

        # Create ChipsDisplay object for displaying chips
        self.chips_path = ChipsDisplay(sw * 0.18, sh * 0.1, chips)
        self.chips_surface = self.chips_path.get_surface()

        self.width = sw * 0.3
        self.height = sh * 0.2

        self.content_width = self.chips_surface.get_width() + self.image_width + self.padding
        self.content_height = max(
            self.chips_surface.get_height() + self.text_surface.get_height() + 5, int(self.image_height) + 1
        )
        # Create a combined surface to hold the image, chips, and text
        self.combined_surface = pygame.Surface((self.width, self.height))
        self.combined_surface.fill((46, 77, 62))  # RGB for dark green

        # Position the image
        self.image_rect = self.image.get_rect(
            topleft=(
                (self.width - self.content_width)/2 + max(self.chips_surface.get_width(), self.text_surface.get_width()) + 10,
                (self.height - self.content_height)/2
            )
        )
        self.combined_surface.blit(self.image, self.image_rect)

        # Position the chips display below the text
        self.chips_rect = self.chips_surface.get_rect(
            topleft=(
                (self.width - self.content_width)/2,
                (self.height - self.content_height)/2 + int(self.text_surface.get_height()) + self.padding
            )
        )
        self.combined_surface.blit(self.chips_surface, self.chips_rect)

        # Position the text
        self.text_rect = self.text_surface.get_rect(
            topleft=((self.width - self.content_width)/2, (self.height - self.content_height)/2)
        )
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def draw(self, screen, x, y):
        # Draw the combined surface on the screen at (x, y)
        screen.blit(self.combined_surface, (x, y))

    def update_chips(self, chips):
        self.chips_path.update_chips(chips)
        self.chips_surface = self.chips_path.get_surface()

        self.combined_surface = pygame.Surface((self.width, self.height))
        self.combined_surface.fill((46, 77, 62)) # RGB for dark green

        self.combined_surface.blit(self.image, self.image_rect)
        self.combined_surface.blit(self.chips_surface, self.chips_rect)
        self.combined_surface.blit(self.text_surface, self.text_rect)


class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value):
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.knob_x = self._value_to_x(initial_value)
        self.is_dragging = False

    def _value_to_x(self, value):
        """Convert slider value to knob position"""
        return self.x + (value - self.min_value) / (self.max_value - self.min_value) * self.width

    def _x_to_value(self, x_pos):
        value = (x_pos - self.x) / self.width * (self.max_value - self.min_value) + self.min_value
        return max(self.min_value, min(self.max_value, value))

    def update(self, event):
        """Handle events and update the slider state"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (self.x <= pygame.mouse.get_pos()[0] <= self.x + self.width and
                self.y - KNOB_RADIUS <= pygame.mouse.get_pos()[1] <= self.y + SLIDER_HEIGHT + KNOB_RADIUS):
                if abs(pygame.mouse.get_pos()[0] - self.knob_x) <= KNOB_RADIUS:
                    self.is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        if event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x = pygame.mouse.get_pos()[0]
                if self.x <= mouse_x <= self.x + self.width:
                    self.knob_x = mouse_x
                    self.value = self._x_to_value(self.knob_x)

    def draw(self, screen):
        """Draw the slider and knob on the screen"""
        # Draw the slider background
        pygame.draw.rect(screen, SLIDER_COLOR, (self.x, self.y, self.width, SLIDER_HEIGHT))

        # Draw the knob
        pygame.draw.circle(screen, KNOB_COLOR, (int(self.knob_x), self.y + SLIDER_HEIGHT // 2), KNOB_RADIUS)

        # Draw the label
        text_surface = font.render(str(round(self.value)), True, WHITE)
        screen.blit(text_surface, (self.x + 40, self.y - 30))

    def get_value(self):
        """Get the current value of the slider"""
        return self.value

    def set_values(self, a, b):
        self.min_value = a
        self.max_value = b

    def set_max_value(self, val):
        self.max_value = val

    def set_min_value(self, val):
        self.min_value = val


class SelfDisplay:
    def __init__(self, x, y, text, img1, img2, chips, padding=5):
        self.x = x
        self.y = y
        self.padding = padding
        self.text = text
        self.image1 = pygame.image.load(img1)
        self.image2 = pygame.image.load(img2)
        image_width = sw * 0.09
        image_height = image_width * 19/14
        self.image1 = pygame.transform.scale(self.image1, (image_width, image_height))
        self.image2 = pygame.transform.scale(self.image2, (image_width, image_height))

        self.text_surface = font.render(self.text, True, (255, 255, 255))

        # Create ChipsDisplay object for displaying chips
        self.chips_path = ChipsDisplay(sw * 0.18, sh * 0.1, chips)
        self.chips_surface = self.chips_path.get_surface()

        # Calculate width and height of the combined surface
        self.width = max(self.chips_surface.get_width(), self.text_surface.get_width(),
                         self.image1.get_width() * 2 + self.padding * 2)

        # Calculate total height: image, chips, text, and padding
        self.height = self.image1.get_height() + self.chips_surface.get_height() + \
                      self.text_surface.get_height() + self.padding * 4

        # Create a combined surface to hold the image, chips, and text
        self.combined_surface = pygame.Surface((self.width, self.height))

        # Position the image
        self.image1_rect = self.image1.get_rect(topleft=(self.padding, self.padding))
        self.combined_surface.blit(self.image1, self.image1_rect)

        self.image2_rect = self.image2.get_rect(topleft=(self.padding * 2 + self.image1.get_width(), self.padding))
        self.combined_surface.blit(self.image2, self.image2_rect)

        # Position the chips display below the image
        self.chips_rect = self.chips_surface.get_rect(
            topleft=(self.padding, self.image1.get_height() + self.padding * 2))
        self.combined_surface.blit(self.chips_surface, self.chips_rect)

        # Position the text below the chips
        self.text_rect = self.text_surface.get_rect(
            topleft=(
                self.padding, self.image1.get_height() + self.chips_surface.get_height() + self.padding * 3))
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def update_img(self, img1, img2):
        h, w = self.image1.get_size()
        img1 = pygame.image.load(img1)
        img1 = pygame.transform.scale(img1, (w, h))
        self.image1_rect = img1.get_rect(topleft=(self.padding, self.padding))
        self.combined_surface.blit(img1, self.image1_rect)

        img2 = pygame.image.load(img2)
        img2 = pygame.transform.scale(img2, (w, h))
        self.image2_rect = img2.get_rect(topleft=(self.padding, self.padding))
        self.combined_surface.blit(img2, self.image2_rect)

    def update_chips(self, chips):
        self.chips_path.update_chips(chips)
        self.chips_surface = self.chips_path.get_surface()

        self.combined_surface = pygame.Surface((self.width, self.height))

        self.combined_surface.blit(self.image1, self.image1_rect)
        self.combined_surface.blit(self.image2, self.image2_rect)
        self.combined_surface.blit(self.chips_surface, self.chips_rect)
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def draw(self, screen):
        # Draw the combined surface on the screen at (x, y)
        screen.blit(self.combined_surface, (self.x, self.y))


class PlayersDisplay:
    def __init__(self):
        self.players = []

    def add_players(self, data):
        for players in data:
            self.players.append(PlayerDisplay(players[0], str(players[1])))

    def clear(self):
        self.players = []

    def remove_player(self, name):
        for player in self.players:
            if player[1] == name:  # Assuming player[1] is the name
                self.players.remove(player)
                break  # Stop once the player is found and removed

    def draw(self, screen):
        if len(self.players) == 1:
            for element in self.players:
                element.draw(screen, sw * 0.45, sh * 0.05)
        elif len(self.players) == 2:
            self.players[0].draw(screen, sw * 0.2, sh * 0.05)
            self.players[1].draw(screen, sw * 0.6, sh * 0.05)

    def get_player(self, i):
        return self.players[i]

    def reset(self):
        self.players = []


class GamesDisplay:
    def __init__(self):
        self.games = []

    def add_game(self, name, game_id):
        display = Button(sw * 0.1, sh * 0.1, name + "'s Game")
        self.games.append([display, game_id])

    def remove_game(self, game_id):
        for game in self.games:
            if game[1] == game_id:
                self.games.remove(game)

    def draw(self, screen):
        i = 1
        for game in self.games:
            game[0].draw(screen, int(sw * 0.2), int(sh * 0.13 * i))
            i += 1

    def get_games(self):
        return self.games


class PlayersLobbyDisplay:
    def __init__(self):
        self.players = []

    def add_players(self, p):
        display = TextDisplay()
        display.update_text(p)
        self.players.append([display, p])

    def clear(self):
        self.players = []

    def count(self):
        return len(self.players)

    def remove_player(self, name):
        for player in self.players:
            if player[1] == name:  # Assuming player[1] is the name
                self.players.remove(player)
                break  # Stop once the player is found and removed

    def draw(self, screen):
        i = 1
        for player in self.players:
            player[0].draw(screen, int(sw * 0.2), int(sh * 0.1 * i))
            i += 1




