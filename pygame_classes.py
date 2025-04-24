import pygame

pygame.init()
screen_info = pygame.display.Info()
sw = screen_info.current_w  # Width of the screen
sh = screen_info.current_h  # Height of the screen
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (211, 211, 211)
BUTTON_NORMAL = (150, 150, 150)
BUTTON_HOVER = (200, 200, 200)
BUTTON_CLICKED = (100, 100, 100)
BUTTON_DISABLED = (100, 100, 100)  # Color for disabled button

# Fonts
font = pygame.font.Font(None, 36)


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
        text_surface = font.render(self.text, True, self.text_color)
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


class CardImg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = 'backs/back04.svg'

    def update_img(self, img):
        self.img = img

    def reset(self):
        self.img = 'backs/back04.svg'

    def draw(self, screen):
        image = pygame.image.load(self.img)
        # scaled_image = pygame.transform.scale(image, (sw*, sh*))
        screen.blit(image, (self.x, self.y))


class TextDisplay:
    def __init__(self, x, y, font_size=36, color=(0, 0, 0), text=''):
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, self.font_size)

    def update_text(self, new_text):
        """Update the text displayed"""
        self.text = new_text

    def draw(self, screen, x, y):
        """Draw the text on the screen"""
        self.x = x
        self.y = y
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.x, self.y))


class ChipsDisplay:
    def __init__(self, text, image='images/golden-apple.png', image_size=(50, 50)):
        # Load and scale the image
        loaded_image = pygame.image.load(image)
        self.image = pygame.transform.scale(loaded_image, image_size)
        self.text = text
        self.padding = 5

        # Render the text
        self.text_surface = font.render(self.text, True, (255, 255, 255))

        # Calculate the combined width and height (using the maximum height)
        self.width = self.image.get_width() + self.text_surface.get_width() + self.padding * 3
        self.height = max(self.image.get_height(), self.text_surface.get_height()) + self.padding * 2  # Fix here

        # Create a surface to combine the image and text
        self.combined_surface = pygame.Surface((self.width, self.height))

        # Blit the image onto the combined surface
        self.image_rect = self.image.get_rect(topleft=(self.padding, (self.height - self.image.get_height()) // 2))
        self.combined_surface.blit(self.image, self.image_rect)

        # Blit the text onto the combined surface (next to the image)
        self.text_rect = self.text_surface.get_rect(
            topleft=(self.image_rect.right + self.padding, (self.height - self.text_surface.get_height()) // 2))
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def update_chips(self, chips):
        # Update the text with the new chip count
        self.text = str(chips)

        # Re-render the text surface
        self.text_surface = font.render(self.text, True, (255, 255, 255))

        # Update the width and height based on the new text
        self.width = self.image.get_width() + self.text_surface.get_width() + self.padding * 3
        self.height = max(self.image.get_height(), self.text_surface.get_height()) + self.padding * 2

        # Create a new surface to combine the image and updated text
        self.combined_surface = pygame.Surface((self.width, self.height))

        # Blit the image onto the combined surface
        self.image_rect = self.image.get_rect(topleft=(self.padding, (self.height - self.image.get_height()) // 2))
        self.combined_surface.blit(self.image, self.image_rect)

        # Blit the text onto the combined surface (next to the image)
        self.text_rect = self.text_surface.get_rect(
            topleft=(self.image_rect.right + self.padding, (self.height - self.text_surface.get_height()) // 2))
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
        self.image = pygame.transform.scale(self.image, (75, 130))

        self.text_surface = font.render(self.text, True, (255, 255, 255))

        # Create ChipsDisplay object for displaying chips
        self.chips_path = ChipsDisplay(chips)
        self.chips_surface = self.chips_path.get_surface()

        # Calculate width and height of the combined surface
        self.width = max(self.chips_surface.get_width(), self.text_surface.get_width(),
                         self.image.get_width())

        # Calculate total height: image, chips, text, and padding
        self.height = self.image.get_height() + self.chips_surface.get_height() + \
                      self.text_surface.get_height() + self.padding * 4

        # Create a combined surface to hold the image, chips, and text
        self.combined_surface = pygame.Surface((self.width, self.height))

        # Position the image
        self.image_rect = self.image.get_rect(topleft=(self.padding, self.padding))
        self.combined_surface.blit(self.image, self.image_rect)

        # Position the chips display below the image
        self.chips_rect = self.chips_surface.get_rect(
            topleft=(self.padding, self.image.get_height() + self.padding * 2))
        self.combined_surface.blit(self.chips_surface, self.chips_rect)

        # Position the text below the chips
        self.text_rect = self.text_surface.get_rect(
            topleft=(
                self.padding, self.image.get_height() + self.chips_surface.get_height() + self.padding * 3))
        self.combined_surface.blit(self.text_surface, self.text_rect)

    def draw(self, screen, x, y):
        # Draw the combined surface on the screen at (x, y)
        screen.blit(self.combined_surface, (x, y))

    def update_chips(self, chips):
        self.chips_path.update_chips(chips)
        self.chips_surface = self.chips_path.get_surface()

        self.combined_surface = pygame.Surface((self.width, self.height))

        self.combined_surface.blit(self.image, self.image_rect)
        self.combined_surface.blit(self.chips_surface, self.chips_rect)
        self.combined_surface.blit(self.text_surface, self.text_rect)


class SelfDisplay:
    def __init__(self, x, y, text, img1, img2, chips, padding=5):
        self.x = x
        self.y = y
        self.padding = padding
        self.text = text
        self.image1 = pygame.image.load(img1)
        self.image2 = pygame.image.load(img2)
        h, w = self.image1.get_size()
        self.image1 = pygame.transform.scale(self.image1, (h * 0.6, w * 0.6))
        self.image2 = pygame.transform.scale(self.image2, (h * 0.6, w * 0.6))

        self.text_surface = font.render(self.text, True, (255, 255, 255))

        # Create ChipsDisplay object for displaying chips
        self.chips_path = ChipsDisplay(chips)
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
        img1 = pygame.transform.scale(img1, (w * 0.6, h * 0.6))
        self.image1_rect = img1.get_rect(topleft=(self.padding, self.padding))
        self.combined_surface.blit(img1, self.image1_rect)

        img2 = pygame.image.load(img2)
        img2 = pygame.transform.scale(img2, (w * 0.6, h * 0.6))
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

    def remove(self, game_id):
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
        display = TextDisplay(int(sw * 0.3), int(sh * 0.1))
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

