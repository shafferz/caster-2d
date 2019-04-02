import pygame as pg
import numpy as np
import PIL.ImageOps
import math
import random

from keras.models import load_model
from PIL import Image

class GameTools:
    def roundline(srf, color, start, end, radius=5):
            dx = end[0]-start[0]
            dy = end[1]-start[1]
            distance = max(abs(dx), abs(dy))
            for i in range(distance):
                x = int( start[0]+float(i)/distance*dx)
                y = int( start[1]+float(i)/distance*dy)
                pg.draw.circle(srf, color, (x, y), radius)

    def predict(srf):
        # Load the model that was already pre-trained
        model = load_model("src/static/file/mnistModel.h5")
        # First, format the image in a bitstring for pillow
        pil_string = pg.image.tostring(srf, "RGB", False)
        # Create the PIL Image object from the RGBA bitstring above
        drawing = Image.frombytes("RGB", (400,400), pil_string)
        # Invert the drawing, since the MNIST data set is white images on black
        drawing = PIL.ImageOps.invert(drawing)
        # Resize the Image to 28x28 from 400x400, removing alpha/RGB channels
        wpercent = (28/float(drawing.size[0]))
        hsize = int((float(drawing.size[1])*float(wpercent)))
        drawing = drawing.resize((28, hsize), Image.ANTIALIAS).convert("L")
        # DEBUG: drawing.show()
        # Convert the drawing to a numpy array for the model, with shape
        # (1,28,28,1)
        drawing_arr = np.array(drawing).reshape(1,28,28,1)
        # Make the prediction on the loaded model
        predictions = model.predict(drawing_arr, batch_size=1)
        return(np.argmax(predictions[0]))

class SpellCrafter(object):
    def __init__(self):
        self.glyph_dict = {
            0: "mana",
            1: "projectile",
            2: "shield",
            3: "curse",
            4: "blessing",
            5: "air",
            6: "earth",
            7: "lightning",
            8: "frost",
            9: "fire"
        }
        # The list of glyphs by name
        self.spell_glyphs = []
        # The number of elements and components respectively.
        self.elements = 0
        self.components = 0
        # The mana cost and strength (damage) of the spell
        self.cost = 0
        self.strength = 10.0
        # The buff/debuff duration of the spell, and the buff multiplier itself
        # Each is a list, as each buff applies specifically to an element
        self.buff = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.debuff = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.buff_timer = [0, 0, 0, 0, 0]
        self.debuff_timer = [0, 0, 0, 0, 0]
        # Two booleans, one to indicate if the spell targets the opponent
        # (on_self) and one to indicate if the spell is a buff/debuff
        self.on_self = False
        self.is_buff = False
        # A key-number pair for the glyp_dict indicating the spell's dominant
        # element, determined by having a majority of that element in the
        # spell's glyphs, and the number of those elements in the spell
        self.dominant_element = (0,0)

    # Add glyphs to spell as cast, return True when successful
    def add_glyph(self, glyph_key):
        # If there is already a component in the spell, remove previous. should
        # be first in list. Also decrease cost proportionally
        if self.components > 0 and glyph_key < 5:
            # if needed in case of misread glyph
            if self.spell_glyphs:
                self.spell_glyphs.pop(0)
                self.components -= 1
                self.cost -= 1
        # If there are already up to 4 elements, remove the last one
        # Also decrease cost proportionally
        if self.elements >= 4 and glyph_key >= 5:
            # if needed in case of misread glyph
            if self.spell_glyphs:
                self.spell_glyphs.pop((len(self.spell_glyphs)-1))
                self.elements -= 1
                self.cost -= 1
        # Count the number of component or element glyphs in the spell as added
        if glyph_key < 5:
            self.components += 1
        else:
            self.elements += 1
        # Add the glyph, increase the cost of the spell,  and sort the glyphs
        self.spell_glyphs.append(self.glyph_dict[glyph_key])
        self.cost += 1
        self.sort_glyphs()

    # Sort lists in the format Mana Glyph - Component Glyph - Element Glyph
    def sort_glyphs(self):
        sorted_list = []
        # First, find any mana glyphs and add them to the sorted list
        for gly in self.spell_glyphs:
            if gly == "mana":
                sorted_list.append(gly)
        # Then, add any component glyphs to sorted list from spell_glyphs
        for gly in self.spell_glyphs:
            for _x in range(1, 5):
                # If the glyph in spell_glyphs is a component glyph, add
                if self.glyph_dict[_x] == gly:
                    sorted_list.append(gly)
        # Finally, do the same for elemental glyphs
        for gly in self.spell_glyphs:
            for _x in range(5, 10):
                # If the glyph in spell_glyphs is an element glyph, add
                if self.glyph_dict[_x] == gly:
                    sorted_list.append(gly)
        # Set the spell_glyphs list to be the new, sorted list
        self.spell_glyphs = sorted_list

    # Check if the spell is empty
    def is_empty(self):
        if len(self.spell_glyphs) == 0:
            return True
        else:
            return False

    # Remove the last glyph in the spell and
    # recalculate number of element/casting glyphs
    def remove_last_glyph(self):
        # Find the removed element's index, so we can decrease elements or
        # components appropriately
        removed_element = self.spell_glyphs.pop()
        for key, value in self.glyph_dict.items():
            if removed_element == value:
                removed_key = key
        if removed_key < 5:
            self.components -= 1
        else:
            self.elements -= 1
        self.cost -= 1
        # Like pop, returns the list element removed
        return removed_element

    # Returns true if and only if spell has a casting glyph (component)
    def has_casting(self):
        # If the spell has glyphs...
        if self.spell_glyphs:
            # And the first of those glyphs is a casting glyph...
            for _x in range(0,5):
                if self.spell_glyphs[0] == self.glyph_dict[_x]:
                    # Return true
                    return True
        # Default return false
        return False

    # Returns true when a spell has the minimum 2 glyphs, at least one
    # casting glyph, and can be afforded to be cast by the player
    def spell_ready(self, mana):
        if len(self.spell_glyphs) < 2:
            return False
        if not self.has_casting():
            return False
        if mana < self.cost:
            return False
        return True

    # Find which element is dominant in the spell
    def find_dominant(self):
        # First glyph should not be an element, and in fact must not be,
        # otherwise this will be wrong
        if self.spell_glyphs[1:]:
            # For each glyph in the spell, count the number of each element
            ctr_list = [0, 0, 0, 0, 0]
            for glyph in self.spell_glyphs[1:]:
                # Glyph is air
                if glyph == self.glyph_dict[5]:
                    ctr_list[0] += 1
                elif glyph == self.glyph_dict[6]:
                    ctr_list[1] += 1
                elif glyph == self.glyph_dict[7]:
                    ctr_list[2] += 1
                elif glyph == self.glyph_dict[8]:
                    ctr_list[3] += 1
                elif glyph == self.glyph_dict[9]:
                    ctr_list[4] += 1
            # Since 0-4 in ctr list represents 5-9 in the dict, the key in the
            # glyph_dict of the dominant element is the index of the highest
            # counter in ctr_list + 5. The number itself is just the max in
            # the list
            dominant_key = ctr_list.index(max(ctr_list))+5
            dominant_num = ctr_list[ctr_list.index(max(ctr_list))]
            self.dominant_element = (dominant_key, dominant_num)

    # converts spell into targets and strengths and so on
    def craft_spell(self):
        # First, determine the spell's dominant element for calculations
        self.find_dominant()
        # Use the casting glyph to determine how the spell functions,
        # i.e., if the spell is a buff/debuff, and the target, etc.,
        if self.spell_glyphs[0] == "mana":
            # If the casting glyph is the mana spell, it will be considered a
            # buff with strength 0 and a target of self
            self.is_buff = True
            self.on_self = True
            self.strength = 0
        elif self.spell_glyphs[0] == "projectile":
            # If the casting glyph is a projectile, it will not be a buff, will
            # target the opponent, and will have a strength variable
            self.is_buff = False
            self.on_self = False
            # Calculate the buff and apply to base strength
            total_modifier = 0.0
            # The buff indices are 0-4, the dominant element key is 5-9,
            # so the applied buff's index applied to the spell is the dominant
            # element key - 5. This holds for the buff_timer also
            dominant_index = (self.dominant_element[0]-5)
            buff = self.buff[dominant_index]
            buff_timer = self.buff_timer[dominant_index]
            # The same holds true for the debuff
            debuff = self.debuff[dominant_index]
            debuff_timer = self.debuff_timer[dominant_index]
            # Next, apply buff/debuff and decrement buff/debuff timers as is
            # appropriate.
            if buff_timer > 0:
                total_modifier += buff
                self.buff_timer[dominant_index] -= 1
            if debuff_timer > 0:
                total_modifier -= debuff
                self.debuff_timer[dominant_index] -= 1
            # Increase the total modifier by 1 + (# of dom. element glyps)-1/3
            # Which, for each of 1, 2, 3, and 4 dominant element glyphs is
            # 1, 1.33, 1.66, and 2 respectively
            total_modifier += 1+((self.dominant_element[1]-1)/3)
            self.strength *= total_modifier
        elif self.spell_glyphs[0] == "shield":
            # If the casting glyph is a shield, it will not be a buff, will
            # target self, and will have a strength comparable to a projectile
            self.is_buff = False
            self.on_self = True
            # Calculate the buff and apply to base strength
            total_modifier = 0.0
            # The buff indices are 0-4, the dominant element key is 5-9,
            # so the applied buff's index applied to the spell is the dominant
            # element key - 5. This holds for the buff_timer also
            dominant_index = (self.dominant_element[0]-5)
            buff = self.buff[dominant_index]
            buff_timer = self.buff_timer[dominant_index]
            # The same holds true for the debuff
            debuff = self.debuff[dominant_index]
            debuff_timer = self.debuff_timer[dominant_index]
            # Next, apply buff/debuff and decrement buff/debuff timers as is
            # appropriate.
            if buff_timer > 0:
                total_modifier += buff
                self.buff_timer[dominant_index] -= 1
            if debuff_timer > 0:
                total_modifier -= debuff
                self.debuff_timer[dominant_index] -= 1
            total_modifier += 1+((self.dominant_element[1]-1)/3)
            self.strength *= total_modifier
        elif self.spell_glyphs[0] == "curse":
            # If the casting glyph is a curse, it will be a (de)buff that
            # targets the opponent, and the strength is the modifier of the buff
            # proportional To the number of elements that the spell uses of it's
            # dominant element
            self.is_buff = True
            self.on_self = False
            # Strength of a curse is 1/4th of the number of the dominant element
            # glyphs in the spell. So 0.25 for 1, 0.5 for 2, and so on.
            # Curses and blessings are unaffected by buffs or debuffs.
            self.strength = ((self.dominant_element[1])/4)
        elif self.spell_glyphs[0] == "blessing":
            # If the casting glyph is a blessing, it will be a buff that
            # targets the caster, and the strength is the modifier of the buff
            # proportional To the number of elements that the spell uses of it's
            # dominant element
            self.is_buff = True
            self.on_self = True
            # Strength of a blessing is comparable to a curse (# of elemental
            # glyphs in the spell). So 0.25 for 1, 0.5 for 2, and so on.
            # Curses and blessings are unaffected by buffs or debuffs.
            self.strength = ((self.dominant_element[1])/4)

    # A simple method for restoring the base values, except for buffs/debuffs,
    # so that the next spell is unaffected by previously cast ones
    def restore_base_values(self):
        # The list of glyphs by name gets emptied
        self.spell_glyphs = []
        # The number of elements and components respectively revert to 0
        self.elements = 0
        self.components = 0
        # The mana cost and strength (damage) of the spell revert to 0
        self.cost = 0
        self.strength = 10.0
        # on_self and is_buff revert to False
        self.on_self = False
        self.is_buff = False
        # The dominant element tuple returns to (0,0)
        self.dominant_element = (0,0)

    # Returns a string with the Spell's title, in the form of:
    # (Superlative) Adjective Element Type
    def spell_title(self):
        # Use the key of the dominant element to get the Spell title's Element
        element = self.glyph_dict[self.dominant_element[0]]
        element = element.capitalize()
        # Choose one of weak or strong for the spell title's Adjective
        adjective = ""
        if self.dominant_element[1] > 2:
            # Strong if more than 2 of the dominant element glyphs exist
            adjective = "Strong"
        else:
            # Weak if less than 3 of the dominant element glyphs exist
            adjective = "Weak"
        # Choose one of lesser or greater for the spell title's Superlative
        superlative = ""
        # Lesser if only 1 dominant element glyph exists
        if self.dominant_element[1] == 1:
            superlative = "Lesser"
        # Greater if all 4 of the dominant element glyphs exist
        if self.dominant_element[1] == 4:
            superlative = "Greater"
        # Finally, the type is the casting glyph, should be the first glyph
        type = self.spell_glyphs[0]
        type = type.capitalize()
        # Put spaces between the words in the title and return it
        title = (superlative + " " + adjective + " " + element + " " + type)
        return(title.lstrip(" "))

    # Generates a random spell of given mana cost, designed to be used by a
    # computer. Always uses one element
    def random_cast(self, mana):
        # Refresh base values
        self.restore_base_values()
        # Choose an element key at random
        element_key = random.randint(5, 9)
        # Add elements up to the remaining about of mana allowance
        for x in range(0, mana-1):
            self.add_glyph(element_key)
        # Randomly add a type of spell
        self.add_glyph(random.randint(0,4))

# A simple Player object that will be used to maintain hitpoint and mana values
class Player(object):
    def __init__(self):
        self.hitpoints = 100
        self.max_mana = 2
        self.mana = self.max_mana
        self.alive = True

    # Take damage to hitpoints equal to dmg
    def hit(self, dmg):
        self.hitpoints -= dmg
        # If hitpoints are reduced to below 1, player dies.
        if self.hitpoints <= 0:
            self.hitpoints = 0
            self.alive = False

    # EOT means end-of-turn, perform functions that would happen for player at
    # the end of the turn (mana increase + refill)
    def eot(self):
        self.max_mana += 1
        self.mana = self.max_mana
