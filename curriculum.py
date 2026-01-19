import random
from flask_babel import gettext as _, lazy_gettext as _l

def generate_question(strand):
    """Generates a random question based on Ontario Gr 1 Curriculum strands."""
    if strand == 'coding':
        engine = CodingMaze()
        return engine.generate()
    elif strand == 'financial':
        return MoneyCounting().generate()
    elif strand == 'placevalue':
        return PlaceValueQuestions().generate()
    elif strand == 'time':
        return TimeTellingQuestions().generate()
    elif strand == 'measurement':
        return MeasurementQuestions().generate()
    elif strand == 'wordproblems':
        return WordProblemQuestions().generate()
    elif strand == 'comparing':
        return ComparingQuestions().generate()
    elif strand == 'skipcounting':
        return SkipCountingQuestions().generate()

    # --- STRAND B: NUMBER (Addition/Subtraction to 50) ---
    elif strand == 'number':
        op = random.choice(['+', '-'])
        if op == '+':
            a = random.randint(1, 25)
            b = random.randint(1, 25)
            question = _("What is") + f" {a} + {b}?"
            answer = a + b
            options = [answer, answer + random.randint(1, 3), answer - random.randint(1, 3)]
        else:
            a = random.randint(10, 50)
            b = random.randint(1, a)  # Ensure positive result
            question = _("What is") + f" {a} - {b}?"
            answer = a - b
            options = [answer, answer + random.randint(1, 5), answer - random.randint(1, 5)]

        # Visual Aid (Emojis) for smaller numbers
        if a <= 10 and b <= 10:
            emoji = random.choice(['🍎', '⭐', '🐸', '🍪'])
            question += f"<br><span style='font-size:2rem'>{' '.join([emoji]*a)} &nbsp;{op}&nbsp; {' '.join([emoji]*b)}</span>"

    # --- STRAND C: ALGEBRA (Patterns & Equalities) ---
    elif strand == 'algebra':
        return AlgebraQuestions().generate()

    # --- STRAND D: DATA (Sorting & Graphs) ---
    elif strand == 'data':
        # Simple Logic: "Which has more?"
        t1, t2 = random.sample([_('Cats') + ' 🐱', _('Dogs') + ' 🐶', _('Birds') + ' 🐦'], 2)
        v1, v2 = random.randint(3, 9), random.randint(3, 9)
        while v1 == v2: v2 = random.randint(3, 9) # Ensure not equal

        # Generate a mini text-graph
        graph = f"{t1}: { '█' * v1 } ({v1})<br>{t2}: { '█' * v2 } ({v2})"
        question = _("Look at the graph. Which group has more?") + f"<br><div class='graph'>{graph}</div>"
        answer = t1 if v1 > v2 else t2
        options = [t1, t2]

    # --- STRAND E: SPATIAL SENSE (Shapes) ---
    elif strand == 'spatial':
        return SpatialQuestions().generate()

    # Handle unknown strands
    else:
        return {"q": "Unknown strand", "a": "", "options": [], "strand": "Error"}

    # Shuffle and deduplicate options properly
    random.shuffle(options)
    seen = set()
    unique_options = []
    for opt in options:
        opt_str = str(opt)
        if opt_str not in seen:
            seen.add(opt_str)
            unique_options.append(opt)
    # Ensure correct answer is always included
    if str(answer) not in [str(o) for o in unique_options]:
        unique_options.append(answer)
    options = unique_options
    random.shuffle(options)

    return {
        "q": question,
        "a": answer,
        "options": options,
        "strand": strand.title()
    }


# ============================================================
# NEW CURRICULUM STRANDS FOR COMPLETE GRADE 1 COVERAGE
# ============================================================

class AlgebraQuestions:
    """Grade 1 Algebra: Patterns, growing/shrinking patterns, equalities"""

    def generate(self):
        mode = random.choice(['pattern_ab', 'pattern_aab', 'pattern_abc', 'growing', 'shrinking', 'missing_number', 'equality'])

        if mode == 'pattern_ab':
            # Simple AB patterns
            patterns = [
                (['🔴', '🔵', '🔴', '🔵', '🔴'], '🔵', ['🔴', '🔵', '🟢']),
                (['🌙', '⭐', '🌙', '⭐', '🌙'], '⭐', ['🌙', '⭐', '🌟']),
                (['🐱', '🐶', '🐱', '🐶', '🐱'], '🐶', ['🐱', '🐶', '🐰']),
                (['▲', '■', '▲', '■', '▲'], '■', ['▲', '■', '●']),
                (['1', '2', '1', '2', '1'], '2', ['1', '2', '3']),
            ]
            pat, correct, opts = random.choice(patterns)
            display = " ".join(pat) + " <b>?</b>"
            question = _("What comes next in the pattern?") + f"<br><div style='font-size:2rem;margin:15px 0;'>{display}</div>"
            options = opts
            answer = correct

        elif mode == 'pattern_aab':
            # AAB patterns
            patterns = [
                (['🔴', '🔴', '🔵', '🔴', '🔴', '🔵', '🔴', '🔴'], '🔵', ['🔴', '🔵', '🟢']),
                (['👏', '👏', '🙌', '👏', '👏', '🙌', '👏', '👏'], '🙌', ['👏', '🙌', '✋']),
                (['🍎', '🍎', '🍊', '🍎', '🍎', '🍊', '🍎', '🍎'], '🍊', ['🍎', '🍊', '🍌']),
            ]
            pat, correct, opts = random.choice(patterns)
            display = " ".join(pat) + " <b>?</b>"
            question = _("What comes next in the pattern?") + f"<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
            options = opts
            answer = correct

        elif mode == 'pattern_abc':
            # ABC patterns
            patterns = [
                (['🔴', '🔵', '🟢', '🔴', '🔵', '🟢', '🔴', '🔵'], '🟢', ['🔴', '🔵', '🟢']),
                (['🍎', '🍊', '🍌', '🍎', '🍊', '🍌', '🍎', '🍊'], '🍌', ['🍎', '🍊', '🍌']),
                (['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'], 'C', ['A', 'B', 'C']),
            ]
            pat, correct, opts = random.choice(patterns)
            display = " ".join(pat) + " <b>?</b>"
            question = _("What comes next in the pattern?") + f"<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
            options = opts
            answer = correct

        elif mode == 'growing':
            # Growing number patterns
            starts = [
                ([1, 2, 3, 4], 5, [5, 6, 4]),
                ([2, 4, 6, 8], 10, [10, 9, 12]),
                ([5, 10, 15, 20], 25, [25, 22, 30]),
                ([1, 3, 5, 7], 9, [9, 8, 11]),
            ]
            seq, correct, opts = random.choice(starts)
            display = ", ".join(str(n) for n in seq) + ", <b>?</b>"
            question = _("What number comes next?") + f"<br><div style='font-size:2rem;margin:15px 0;'>{display}</div>"
            options = [str(o) for o in opts]
            answer = str(correct)

        elif mode == 'shrinking':
            # Shrinking patterns
            starts = [
                ([10, 9, 8, 7], 6, [6, 5, 8]),
                ([20, 18, 16, 14], 12, [12, 10, 13]),
                ([15, 12, 9, 6], 3, [3, 4, 0]),
            ]
            seq, correct, opts = random.choice(starts)
            display = ", ".join(str(n) for n in seq) + ", <b>?</b>"
            question = _("The numbers are getting smaller. What comes next?") + f"<br><div style='font-size:2rem;margin:15px 0;'>{display}</div>"
            options = [str(o) for o in opts]
            answer = str(correct)

        elif mode == 'missing_number':
            # Find the missing number in addition
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            total = a + b
            question = _("Find the missing number:") + f"<br><div style='font-size:2.5rem;margin:15px 0;'>{a} + <b>?</b> = {total}</div>"
            answer = str(b)
            options = [str(b), str(b + 1), str(b - 1) if b > 1 else str(b + 2)]

        else:  # equality
            # Balance/equality
            a = random.randint(2, 8)
            b = random.randint(1, a - 1)
            c = a - b
            question = _("Make both sides equal:") + f"<br><div style='font-size:2rem;margin:15px 0;'>{a} = {b} + <b>?</b></div>"
            answer = str(c)
            options = [str(c), str(c + 1), str(c - 1) if c > 1 else str(c + 2)]

        random.shuffle(options)

        return {
            "type": "algebra",
            "strand": _("Patterns"),
            "q": question,
            "a": answer,
            "options": options
        }


class SpatialQuestions:
    """Grade 1 Spatial Sense: 2D shapes, 3D shapes, position, symmetry"""

    # SVG shapes with distinct proportions
    SHAPES_2D = {
        'Triangle': '<svg width="50" height="45" viewBox="0 0 50 45"><polygon points="25,2 48,43 2,43" fill="#e74c3c"/></svg>',
        'Circle': '<svg width="50" height="50" viewBox="0 0 50 50"><circle cx="25" cy="25" r="22" fill="#3498db"/></svg>',
        'Square': '<svg width="50" height="50" viewBox="0 0 50 50"><rect x="3" y="3" width="44" height="44" fill="#2ecc71"/></svg>',
        'Rectangle': '<svg width="70" height="40" viewBox="0 0 70 40"><rect x="2" y="2" width="66" height="36" fill="#9b59b6"/></svg>',
    }

    SHAPES_3D = {
        'Sphere': '<svg width="60" height="60" viewBox="0 0 60 60"><defs><radialGradient id="sg" cx="30%" cy="30%"><stop offset="0%" style="stop-color:#5dade2"/><stop offset="100%" style="stop-color:#2874a6"/></radialGradient></defs><circle cx="30" cy="30" r="26" fill="url(#sg)"/></svg>',
        'Cube': '<svg width="60" height="60" viewBox="0 0 60 60"><polygon points="10,20 30,10 50,20 50,45 30,55 10,45" fill="#58d68d" stroke="#27ae60" stroke-width="2"/><polygon points="10,20 30,30 30,55 10,45" fill="#2ecc71"/><polygon points="30,30 50,20 50,45 30,55" fill="#1d8348"/><line x1="30" y1="10" x2="30" y2="30" stroke="#27ae60" stroke-width="2"/></svg>',
        'Cylinder': '<svg width="50" height="65" viewBox="0 0 50 65"><ellipse cx="25" cy="12" rx="20" ry="10" fill="#af7ac5"/><rect x="5" y="12" width="40" height="40" fill="#9b59b6"/><ellipse cx="25" cy="52" rx="20" ry="10" fill="#7d3c98"/><ellipse cx="25" cy="12" rx="20" ry="10" fill="#d7bde2"/></svg>',
        'Cone': '<svg width="50" height="60" viewBox="0 0 50 60"><polygon points="25,5 45,50 5,50" fill="#f5b041"/><ellipse cx="25" cy="50" rx="20" ry="8" fill="#d68910"/></svg>',
    }

    def _get_shape_name(self, key):
        """Get translated shape name"""
        shape_names = {
            'Triangle': _('Triangle'),
            'Circle': _('Circle'),
            'Square': _('Square'),
            'Rectangle': _('Rectangle'),
            'Sphere': _('Sphere'),
            'Cube': _('Cube'),
            'Cylinder': _('Cylinder'),
            'Cone': _('Cone'),
        }
        return shape_names.get(key, key)

    def generate(self):
        mode = random.choice(['identify_2d', 'identify_2d', 'identify_3d', 'position', 'count_sides', 'same_shape'])

        if mode == 'identify_2d':
            target_key = random.choice(list(self.SHAPES_2D.keys()))
            target_name = self._get_shape_name(target_key)
            question = _("Which one is a") + f" <b>{target_name}</b>?"
            answer = self.SHAPES_2D[target_key]
            options = list(self.SHAPES_2D.values())
            random.shuffle(options)

        elif mode == 'identify_3d':
            target_key = random.choice(list(self.SHAPES_3D.keys()))
            target_name = self._get_shape_name(target_key)
            question = _("Which one is a") + f" <b>{target_name}</b>?"
            answer = self.SHAPES_3D[target_key]
            options = list(self.SHAPES_3D.values())
            random.shuffle(options)

        elif mode == 'position':
            positions = [
                ('above', '🏠<br>🚗', _('house'), _('car')),
                ('below', '🌳<br>🐕', _('tree'), _('dog')),
                ('beside', '🧸 📚', _('teddy bear'), _('book')),
                ('between', '🍎 🍌 🍊', _('banana'), _('apple and orange')),
            ]
            pos_word, visual, target, reference = random.choice(positions)
            pos_word_translated = {
                'above': _('above'),
                'below': _('below'),
                'beside': _('beside'),
                'between': _('between'),
            }[pos_word]
            question = _("Look at the picture:") + f"<br><div style='font-size:2.5rem;margin:15px 0;'>{visual}</div><br>" + _("What is") + f" <b>{pos_word_translated}</b> " + _("the") + f" {reference}?"
            answer = target
            all_items = [_('house'), _('car'), _('tree'), _('dog'), _('teddy bear'), _('book'), _('banana'), _('apple'), _('orange')]
            wrong = [i for i in all_items if i != target][:2]
            options = [target] + wrong
            random.shuffle(options)

        elif mode == 'count_sides':
            side_shapes = [
                ('Triangle', 3, self.SHAPES_2D['Triangle']),
                ('Square', 4, self.SHAPES_2D['Square']),
                ('Rectangle', 4, self.SHAPES_2D['Rectangle']),
            ]
            name, sides, svg = random.choice(side_shapes)
            question = _("How many sides does this shape have?") + f"<br><div style='margin:15px 0;'>{svg}</div>"
            answer = str(sides)
            options = ['3', '4', '5']
            if answer not in options:
                options[2] = answer
            random.shuffle(options)

        else:  # same_shape
            shape_pairs = [
                ('Triangle', '<svg width="40" height="35"><polygon points="20,2 38,33 2,33" fill="#e74c3c"/></svg>', '<svg width="50" height="45"><polygon points="25,2 48,43 2,43" fill="#c0392b"/></svg>'),
                ('Circle', '<svg width="35" height="35"><circle cx="17" cy="17" r="15" fill="#3498db"/></svg>', '<svg width="50" height="50"><circle cx="25" cy="25" r="22" fill="#2980b9"/></svg>'),
                ('Square', '<svg width="35" height="35"><rect x="2" y="2" width="31" height="31" fill="#2ecc71"/></svg>', '<svg width="50" height="50"><rect x="2" y="2" width="46" height="46" fill="#27ae60"/></svg>'),
            ]
            name, small, big = random.choice(shape_pairs)
            translated_name = self._get_shape_name(name)
            question = _("These shapes are both the same type. What shape are they?") + f"<br><div style='margin:15px 0;display:flex;justify-content:center;gap:20px;align-items:center;'>{small}{big}</div>"
            answer = translated_name
            options = [self._get_shape_name('Triangle'), self._get_shape_name('Circle'), self._get_shape_name('Square'), self._get_shape_name('Rectangle')]
            options = [o for o in options if o != translated_name][:2] + [translated_name]
            random.shuffle(options)

        return {
            "type": "spatial",
            "strand": _("Spatial"),
            "q": question,
            "a": answer,
            "options": options
        }


class PlaceValueQuestions:
    """Grade 1 Place Value: Understanding tens and ones (numbers to 50)"""

    def generate(self):
        mode = random.choice(['identify_tens', 'identify_ones', 'compose', 'decompose'])

        if mode == 'identify_tens':
            num = random.randint(10, 50)
            tens = num // 10
            ones = num % 10
            # Visual: Base-10 blocks (brown squares for tens, yellow for ones)
            blocks_visual = "🟫 " * tens + "🟨 " * ones if ones > 0 else "🟫 " * tens
            question = _("How many tens are in the number") + f" {num}?<br><div style='font-size:1.5rem;margin:10px 0'>{blocks_visual.strip()}</div>"
            answer = str(tens)
            options = [str(tens), str(tens + 1) if tens < 5 else str(tens - 1), str(ones)]

        elif mode == 'identify_ones':
            num = random.randint(10, 50)
            tens = num // 10
            ones = num % 10
            blocks_visual = "🟫 " * tens + "🟨 " * ones if ones > 0 else "🟫 " * tens
            question = _("How many ones are in the number") + f" {num}?<br><div style='font-size:1.5rem;margin:10px 0'>{blocks_visual.strip()}</div>"
            answer = str(ones)
            options = [str(ones), str(tens), str((ones + 2) % 10)]

        elif mode == 'compose':
            tens = random.randint(1, 4)
            ones = random.randint(0, 9)
            correct = tens * 10 + ones
            tens_word = _("tens")
            ones_word = _("ones")
            question = f"<b>{tens} {tens_word}</b> " + _("and") + f" <b>{ones} {ones_word}</b> = ?"
            answer = str(correct)
            options = [str(correct), str(correct + 10), str(correct + 1) if ones < 9 else str(correct - 1)]

        else:  # decompose
            num = random.randint(11, 49)
            tens = num // 10
            ones = num % 10
            question = _("Break apart") + f" <b>{num}</b> " + _("into tens and ones:")
            tens_word = _("tens")
            ones_word = _("ones")
            answer = f"{tens} {tens_word}, {ones} {ones_word}"
            options = [
                f"{tens} {tens_word}, {ones} {ones_word}",
                f"{tens + 1} {tens_word}, {ones} {ones_word}",
                f"{tens} {tens_word}, {ones + 1 if ones < 9 else ones - 1} {ones_word}"
            ]

        # Deduplicate options
        seen = set()
        unique = []
        for opt in options:
            if opt not in seen:
                seen.add(opt)
                unique.append(opt)
        if answer not in unique:
            unique.append(answer)
        random.shuffle(unique)

        return {
            "type": "placevalue",
            "strand": _("Place Value"),
            "q": question,
            "a": answer,
            "options": unique
        }


class TimeTellingQuestions:
    """Grade 1 Time: Reading o'clock and half-past on analog clocks"""

    def _draw_clock(self, hour, minutes):
        """Generate an SVG analog clock face."""
        # Hour hand angle (30 degrees per hour + 0.5 per minute)
        hour_angle = (hour % 12) * 30 + minutes * 0.5
        # Minute hand angle (6 degrees per minute)
        min_angle = minutes * 6

        return f'''
        <svg class="clock" width="140" height="140" viewBox="0 0 100 100" style="display:block;margin:15px auto;">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="3"/>
            <text x="50" y="18" text-anchor="middle" font-size="12" font-weight="bold">12</text>
            <text x="82" y="54" text-anchor="middle" font-size="12" font-weight="bold">3</text>
            <text x="50" y="92" text-anchor="middle" font-size="12" font-weight="bold">6</text>
            <text x="18" y="54" text-anchor="middle" font-size="12" font-weight="bold">9</text>
            <line x1="50" y1="50" x2="50" y2="28" stroke="#333" stroke-width="4" stroke-linecap="round" transform="rotate({hour_angle}, 50, 50)"/>
            <line x1="50" y1="50" x2="50" y2="18" stroke="#666" stroke-width="2" stroke-linecap="round" transform="rotate({min_angle}, 50, 50)"/>
            <circle cx="50" cy="50" r="4" fill="#333"/>
        </svg>
        '''

    def generate(self):
        mode = random.choice(['read_oclock', 'read_half', 'activity'])

        if mode == 'read_oclock':
            hour = random.randint(1, 12)
            clock_html = self._draw_clock(hour, 0)
            question = _("What time does the clock show?") + clock_html
            answer = f"{hour}:00"
            other_hour = (hour % 12) + 1
            options = [f"{hour}:00", f"{other_hour}:00", f"{hour}:30"]

        elif mode == 'read_half':
            hour = random.randint(1, 12)
            clock_html = self._draw_clock(hour, 30)
            question = _("What time does the clock show?") + clock_html
            answer = f"{hour}:30"
            other_hour = (hour % 12) + 1
            options = [f"{hour}:30", f"{hour}:00", f"{other_hour}:00"]

        else:  # activity matching
            activities = [
                (_("wake up for school"), "7:00"),
                (_("eat lunch"), "12:00"),
                (_("eat dinner"), "6:00"),
                (_("go to bed"), "8:00"),
            ]
            activity, time = random.choice(activities)
            question = _("What time do most kids") + f" <b>{activity}</b>?"
            answer = time
            all_times = ["7:00", "12:00", "6:00", "8:00", "3:00"]
            options = [t for t in all_times if t != time][:2] + [time]

        random.shuffle(options)
        return {
            "type": "time",
            "strand": _("Time"),
            "q": question,
            "a": answer,
            "options": options
        }


class MeasurementQuestions:
    """Grade 1 Measurement: Comparing lengths and using non-standard units"""

    def generate(self):
        mode = random.choice(['compare', 'count_units', 'order'])

        if mode == 'compare':
            items = [
                (_("pencil"), 5, "✏️"),
                (_("crayon"), 3, "🖍️"),
                (_("marker"), 6, "🖊️"),
                (_("eraser"), 2, "🧽"),
                (_("book"), 8, "📕"),
            ]
            item1 = random.choice(items)
            item2 = random.choice([i for i in items if i[0] != item1[0]])

            bar1 = "█" * item1[1]
            bar2 = "█" * item2[1]

            question = _("Which is longer?") + f'''<br>
            <div style="text-align:left;margin:15px;font-family:monospace;">
                <div>{item1[2]} {item1[0].title()}: <span style="color:#3498db">{bar1}</span></div>
                <div>{item2[2]} {item2[0].title()}: <span style="color:#e74c3c">{bar2}</span></div>
            </div>'''

            if item1[1] > item2[1]:
                answer = item1[0].title()
            else:
                answer = item2[0].title()
            options = [item1[0].title(), item2[0].title(), _("They are the same")]

        elif mode == 'count_units':
            units = random.randint(3, 7)
            unit_emoji = random.choice(["📎", "🧱", "📏"])
            line = "━" * (units * 2)

            question = _("How many") + f" {unit_emoji} " + _("long is this line?") + f'''<br>
            <div style="margin:15px 0;font-size:1.5rem;">{line}</div>
            <div style="font-size:1.3rem;">{unit_emoji * units}</div>'''

            answer = str(units)
            options = [str(units), str(units + 1), str(units - 1)]

        else:  # order by size
            question = _("Put these in order from shortest to longest:") + "<br><br>🐜 " + _("Ant") + ", 🐱 " + _("Cat") + ", 🐘 " + _("Elephant")
            answer = _("Ant") + ", " + _("Cat") + ", " + _("Elephant")
            options = [
                _("Ant") + ", " + _("Cat") + ", " + _("Elephant"),
                _("Elephant") + ", " + _("Cat") + ", " + _("Ant"),
                _("Cat") + ", " + _("Ant") + ", " + _("Elephant")
            ]

        random.shuffle(options)
        return {
            "type": "measurement",
            "strand": _("Measurement"),
            "q": question,
            "a": answer,
            "options": options
        }


class WordProblemQuestions:
    """Grade 1 Word Problems: Story-based addition and subtraction"""

    def generate(self):
        mode = random.choice(['addition', 'subtraction'])

        if mode == 'addition':
            templates = [
                (_("Sara has {a} apples. Mom gives her {b} more. How many apples does Sara have now?"), "🍎"),
                (_("There are {a} birds in a tree. {b} more birds fly in. How many birds are there now?"), "🐦"),
                (_("Tom has {a} cookies. He bakes {b} more. How many cookies does he have?"), "🍪"),
                (_("You have {a} stickers. Your friend gives you {b} more. How many stickers do you have?"), "⭐"),
            ]
            template, emoji = random.choice(templates)
            a = random.randint(2, 8)
            b = random.randint(1, 5)
            answer = a + b

            question = template.format(a=a, b=b)
            visual = f"<div style='font-size:1.5rem;margin:10px 0'>{emoji * a} + {emoji * b}</div>"
            question = f"{question}{visual}"

        else:  # subtraction
            templates = [
                (_("You have {a} balloons. {b} pop! How many balloons are left?"), "🎈"),
                (_("There are {a} cookies. You eat {b}. How many cookies are left?"), "🍪"),
                (_("{a} frogs are on a log. {b} jump away. How many frogs are still on the log?"), "🐸"),
                (_("Mom baked {a} cupcakes. You ate {b}. How many are left?"), "🧁"),
            ]
            template, emoji = random.choice(templates)
            a = random.randint(5, 10)
            b = random.randint(1, a - 1)
            answer = a - b

            question = template.format(a=a, b=b)

        options = [str(answer), str(answer + 1), str(answer - 1) if answer > 1 else str(answer + 2)]
        random.shuffle(options)

        return {
            "type": "wordproblems",
            "strand": _("Word Problems"),
            "q": question,
            "a": str(answer),
            "options": options
        }


class ComparingQuestions:
    """Grade 1 Comparing Numbers: Greater than, less than, equal"""

    def generate(self):
        mode = random.choice(['greater_less', 'fill_symbol', 'number_line'])

        if mode == 'greater_less':
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            while a == b:
                b = random.randint(1, 50)

            question = _("Which number is greater?") + f"<br><div style='font-size:2.5rem;margin:15px 0;'>{a} &nbsp;&nbsp; " + _("or") + f" &nbsp;&nbsp; {b}</div>"
            answer = str(max(a, b))
            options = [str(a), str(b), _("They are equal")]

        elif mode == 'fill_symbol':
            a = random.randint(1, 30)
            b = random.randint(1, 30)

            question = _("Fill in the blank:") + f"<br><div style='font-size:2.5rem;margin:15px 0;'>{a} &nbsp; ⬜ &nbsp; {b}</div><p>" + _("Choose the correct symbol:") + "</p>"

            if a > b:
                answer = ">"
            elif a < b:
                answer = "<"
            else:
                answer = "="
            options = [">", "<", "="]

        else:  # number_line
            target = random.randint(5, 15)
            question = _("Look at the number line. Which number is greater than") + f" {target}?<br>"
            question += f'''<div style="margin:15px 0;font-family:monospace;">
                ◀─ {target-3} ─ {target-2} ─ {target-1} ─ <b>{target}</b> ─ {target+1} ─ {target+2} ─ {target+3} ─▶
            </div>'''
            answer = str(target + random.randint(1, 3))
            wrong1 = str(target - random.randint(1, 2))
            wrong2 = str(target)
            options = [answer, wrong1, wrong2]

        random.shuffle(options)
        return {
            "type": "comparing",
            "strand": _("Comparing"),
            "q": question,
            "a": answer,
            "options": options
        }


class SkipCountingQuestions:
    """Grade 1 Skip Counting: Counting by 2s, 5s, and 10s"""

    def generate(self):
        skip = random.choice([2, 5, 10])
        mode = random.choice(['next_number', 'fill_gap', 'count_objects'])

        if mode == 'next_number':
            start = random.randint(0, 3) * skip
            sequence = [start + skip * i for i in range(4)]
            display = ", ".join(str(n) for n in sequence) + ", ?"

            question = _("Count by") + f" <b>{skip}s</b>. " + _("What comes next?") + f"<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
            answer = str(sequence[-1] + skip)
            options = [
                str(sequence[-1] + skip),
                str(sequence[-1] + 1),
                str(sequence[-1] + skip + skip)
            ]

        elif mode == 'fill_gap':
            start = random.randint(0, 2) * skip
            sequence = [start + skip * i for i in range(5)]
            gap_idx = random.randint(1, 3)
            missing = sequence[gap_idx]
            display_seq = [str(n) if i != gap_idx else "?" for i, n in enumerate(sequence)]
            display = ", ".join(display_seq)

            question = _("Count by") + f" <b>{skip}s</b>. " + _("What is the missing number?") + f"<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
            answer = str(missing)
            options = [str(missing), str(missing + 1), str(missing - 1)]

        else:  # count_objects
            count = random.randint(3, 6)
            if skip == 2:
                emoji = "👟"
                item = _("pairs of shoes")
            elif skip == 5:
                emoji = "🖐️"
                item = _("hands (5 fingers each)")
            else:  # 10
                emoji = "🔟"
                item = _("groups of 10")

            total = count * skip
            question = _("Count by") + f" <b>{skip}s</b>. " + _("How many in total?") + f"<br><div style='font-size:2rem;margin:15px 0;'>{emoji * count}</div><p>{count} {item}</p>"
            answer = str(total)
            options = [str(total), str(total + skip), str(total - skip) if total > skip else str(total + skip * 2)]

        # Deduplicate
        seen = set()
        unique = []
        for opt in options:
            if opt not in seen:
                seen.add(opt)
                unique.append(opt)
        if answer not in unique:
            unique.append(answer)
        random.shuffle(unique)

        return {
            "type": "skipcounting",
            "strand": _("Skip Counting"),
            "q": question,
            "a": answer,
            "options": unique
        }


class MoneyCounting:
    def __init__(self):
        # Canadian Coins: (Value in cents, CSS Class, Label for Accessibility)
        self.coins = [
            {"val": 5,   "css": "nickel",   "name": _("Nickel")},
            {"val": 10,  "css": "dime",     "name": _("Dime")},
            {"val": 25,  "css": "quarter",  "name": _("Quarter")},
            {"val": 100, "css": "loonie",   "name": _("Loonie") + " ($1)"},
            {"val": 200, "css": "toonie",   "name": _("Toonie") + " ($2)"}
        ]

    def generate(self):
        # 50% Chance: Identify a single coin
        # 50% Chance: Count a small pile
        mode = random.choice(['identify', 'count'])

        if mode == 'identify':
            target = random.choice(self.coins)
            question_html = f"""
                <div class='coin-container'>
                    <div class='coin {target['css']}'></div>
                </div>
                <br>""" + _("What is this coin?")

            answer = target['name']
            # Distractors: Other coin names
            options = [c['name'] for c in self.coins if c['name'] != answer]
            random.shuffle(options)
            options = options[:2] + [answer]
            random.shuffle(options)

            return {
                "type": "financial",
                "strand": _("Financial"),
                "q": question_html,
                "a": answer,
                "options": options
            }

        else: # mode == 'count'
            # Grade 1 Limit: Keep total under $5 (500 cents) generally
            # Generate 2-5 coins
            pile = []
            for _ in range(random.randint(2, 4)):
                pile.append(random.choice(self.coins))

            total_cents = sum(c['val'] for c in pile)

            # Format the answer ($3.25 or 45¢)
            if total_cents >= 100:
                answer_str = f"${total_cents/100:.2f}"
            else:
                answer_str = f"{total_cents}¢"

            # Generate the Visual Pile
            coins_html = ""
            for c in pile:
                coins_html += f"<div class='coin {c['css']}'></div>"

            question_html = _("How much money is this?") + f"<br><div class='coin-container'>{coins_html}</div>"

            # Generate Smart Distractors (off by 5, 10, or 25 cents)
            distractors = set()
            while len(distractors) < 2:
                offset = random.choice([-5, 5, -10, 10, -25, 25])
                fake_val = total_cents + offset
                if fake_val > 0 and fake_val != total_cents:
                    if fake_val >= 100:
                        distractors.add(f"${fake_val/100:.2f}")
                    else:
                        distractors.add(f"{fake_val}¢")

            options = list(distractors) + [answer_str]
            random.shuffle(options)

            return {
                "type": "financial",
                "strand": _("Financial"),
                "q": question_html,
                "a": answer_str,
                "options": options
            }


class CodingQuestions:
    """Grade 1 Coding: Sequential thinking, debugging, conditionals, loops"""

    def __init__(self):
        self.grid_size = 3
        self.moves = {
            '⬆️': (-1, 0),
            '⬇️': (1, 0),
            '⬅️': (0, -1),
            '➡️': (0, 1)
        }

    def generate(self):
        mode = random.choice(['maze', 'maze', 'debug', 'conditional', 'repeat', 'sequence'])
        if mode == 'maze':
            return self._generate_maze()
        elif mode == 'debug':
            return self._generate_debug()
        elif mode == 'conditional':
            return self._generate_conditional()
        elif mode == 'repeat':
            return self._generate_repeat()
        else:
            return self._generate_sequence()

    def _generate_maze(self):
        """Get the Robot to the Star puzzle."""
        cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        start, end = random.sample(cells, 2)

        path = []
        curr_r, curr_c = start
        target_r, target_c = end

        while curr_r != target_r:
            if target_r > curr_r:
                path.append('⬇️')
                curr_r += 1
            else:
                path.append('⬆️')
                curr_r -= 1

        while curr_c != target_c:
            if target_c > curr_c:
                path.append('➡️')
                curr_c += 1
            else:
                path.append('⬅️')
                curr_c -= 1

        correct_code = " ".join(path)
        options = {correct_code}

        while len(options) < 3:
            fake_path = path.copy()
            if len(fake_path) > 1:
                random.shuffle(fake_path)
            else:
                fake_path.append(random.choice(list(self.moves.keys())))
            fake_str = " ".join(fake_path)
            if fake_str != correct_code:
                options.add(fake_str)

        grid_html = "<table class='maze-grid'>"
        for r in range(self.grid_size):
            grid_html += "<tr>"
            for c in range(self.grid_size):
                cell_content = "⬜"
                if (r, c) == start:
                    cell_content = "🤖"
                elif (r, c) == end:
                    cell_content = "⭐"
                grid_html += f"<td>{cell_content}</td>"
            grid_html += "</tr>"
        grid_html += "</table>"

        return {
            "type": "coding",
            "strand": _("Coding"),
            "q": _("Which code gets the Robot to the Star?") + f"<br>{grid_html}",
            "a": correct_code,
            "options": list(options)
        }

    def _generate_debug(self):
        """Find the bug in the code."""
        scenarios = [
            {
                "task": _("The robot wants to go RIGHT then DOWN."),
                "buggy": "⬇️ ➡️",
                "correct": "➡️ ⬇️",
                "bug_explanation": _("The steps are in the wrong order!")
            },
            {
                "task": _("The robot wants to go UP twice."),
                "buggy": "⬆️ ⬇️",
                "correct": "⬆️ ⬆️",
                "bug_explanation": _("The second step goes the wrong way!")
            },
            {
                "task": _("The robot wants to go LEFT then LEFT again."),
                "buggy": "⬅️ ➡️",
                "correct": "⬅️ ⬅️",
                "bug_explanation": _("The second step goes the wrong way!")
            },
            {
                "task": _("The robot wants to go DOWN then RIGHT."),
                "buggy": "➡️ ⬇️",
                "correct": "⬇️ ➡️",
                "bug_explanation": _("The steps are backwards!")
            },
        ]
        scenario = random.choice(scenarios)

        question = f'''
            {scenario["task"]}<br><br>
            <div style="background:#fff3cd;padding:15px;border-radius:10px;margin:10px 0;">
                <b>''' + _("Code:") + f'''</b> <span style="font-size:1.5rem;">{scenario["buggy"]}</span>
            </div>
            <p>''' + _("This code has a bug! Which code is correct?") + '''</p>
        '''

        wrong_options = [
            scenario["buggy"],
            scenario["buggy"].replace("⬆️", "⬇️") if "⬆️" in scenario["buggy"] else scenario["buggy"] + " ➡️"
        ]
        options = [scenario["correct"]] + [w for w in wrong_options if w != scenario["correct"]][:2]
        random.shuffle(options)

        return {
            "type": "coding",
            "strand": _("Coding"),
            "q": question,
            "a": scenario["correct"],
            "options": options
        }

    def _generate_conditional(self):
        """If-then scenarios for Grade 1."""
        scenarios = [
            {
                "condition": _("If it is sunny, go to the park. If it is rainy, stay home."),
                "weather": _("sunny") + " ☀️",
                "answer": _("Go to the park"),
                "options": [_("Go to the park"), _("Stay home"), _("Go to school")]
            },
            {
                "condition": _("If it is sunny, go to the park. If it is rainy, stay home."),
                "weather": _("rainy") + " 🌧️",
                "answer": _("Stay home"),
                "options": [_("Go to the park"), _("Stay home"), _("Go swimming")]
            },
            {
                "condition": _("If the light is green, walk. If the light is red, stop."),
                "weather": _("green") + " 🟢",
                "answer": _("Walk"),
                "options": [_("Walk"), _("Stop"), _("Run")]
            },
            {
                "condition": _("If the light is green, walk. If the light is red, stop."),
                "weather": _("red") + " 🔴",
                "answer": _("Stop"),
                "options": [_("Walk"), _("Stop"), _("Jump")]
            },
            {
                "condition": _("If you are hungry, eat food. If you are thirsty, drink water."),
                "weather": _("hungry") + " 🍽️",
                "answer": _("Eat food"),
                "options": [_("Eat food"), _("Drink water"), _("Go to sleep")]
            },
            {
                "condition": _("If you are hungry, eat food. If you are thirsty, drink water."),
                "weather": _("thirsty") + " 💧",
                "answer": _("Drink water"),
                "options": [_("Eat food"), _("Drink water"), _("Watch TV")]
            },
        ]
        scenario = random.choice(scenarios)

        question = f'''
            <div style="background:#e8f4fc;padding:15px;border-radius:10px;margin:10px 0;">
                <b>''' + _("Rule:") + f'''</b> {scenario["condition"]}
            </div>
            <p>''' + _("Today it is") + f''' <b>{scenario["weather"]}</b>. ''' + _("What should you do?") + '''</p>
        '''

        options = scenario["options"].copy()
        random.shuffle(options)

        return {
            "type": "coding",
            "strand": _("Coding"),
            "q": question,
            "a": scenario["answer"],
            "options": options
        }

    def _generate_repeat(self):
        """Loop/repeat patterns."""
        patterns = [
            {
                "instruction": _("Do this 3 times: Clap"),
                "answer": "👏 👏 👏",
                "options": ["👏 👏 👏", "👏 👏", "👏 👏 👏 👏"]
            },
            {
                "instruction": _("Do this 2 times: Jump then Spin"),
                "answer": "⬆️ 🔄 ⬆️ 🔄",
                "options": ["⬆️ 🔄 ⬆️ 🔄", "⬆️ ⬆️ 🔄 🔄", "⬆️ 🔄"]
            },
            {
                "instruction": _("Do this 4 times: Step right"),
                "answer": "➡️ ➡️ ➡️ ➡️",
                "options": ["➡️ ➡️ ➡️ ➡️", "➡️ ➡️ ➡️", "➡️ ➡️"]
            },
            {
                "instruction": _("Do this 2 times: Wave"),
                "answer": "👋 👋",
                "options": ["👋 👋", "👋 👋 👋", "👋"]
            },
        ]
        pattern = random.choice(patterns)

        question = f'''
            <div style="background:#f0fff0;padding:15px;border-radius:10px;margin:10px 0;">
                <b>''' + _("Instruction:") + f'''</b> {pattern["instruction"]}
            </div>
            <p>''' + _("What does this look like?") + '''</p>
        '''

        options = pattern["options"].copy()
        random.shuffle(options)

        return {
            "type": "coding",
            "strand": _("Coding"),
            "q": question,
            "a": pattern["answer"],
            "options": options
        }

    def _generate_sequence(self):
        """Order the steps correctly."""
        sequences = [
            {
                "task": _("How do you make a sandwich?"),
                "correct": _("Get bread") + " → " + _("Add filling") + " → " + _("Close sandwich"),
                "options": [
                    _("Get bread") + " → " + _("Add filling") + " → " + _("Close sandwich"),
                    _("Add filling") + " → " + _("Get bread") + " → " + _("Close sandwich"),
                    _("Close sandwich") + " → " + _("Get bread") + " → " + _("Add filling")
                ]
            },
            {
                "task": _("How do you brush your teeth?"),
                "correct": _("Get toothbrush") + " → " + _("Add toothpaste") + " → " + _("Brush teeth"),
                "options": [
                    _("Get toothbrush") + " → " + _("Add toothpaste") + " → " + _("Brush teeth"),
                    _("Brush teeth") + " → " + _("Add toothpaste") + " → " + _("Get toothbrush"),
                    _("Add toothpaste") + " → " + _("Brush teeth") + " → " + _("Get toothbrush")
                ]
            },
            {
                "task": _("How do you get dressed?"),
                "correct": _("Put on shirt") + " → " + _("Put on pants") + " → " + _("Put on shoes"),
                "options": [
                    _("Put on shirt") + " → " + _("Put on pants") + " → " + _("Put on shoes"),
                    _("Put on shoes") + " → " + _("Put on shirt") + " → " + _("Put on pants"),
                    _("Put on pants") + " → " + _("Put on shoes") + " → " + _("Put on shirt")
                ]
            },
            {
                "task": _("How do you plant a seed?"),
                "correct": _("Dig a hole") + " → " + _("Put in seed") + " → " + _("Cover with soil"),
                "options": [
                    _("Dig a hole") + " → " + _("Put in seed") + " → " + _("Cover with soil"),
                    _("Put in seed") + " → " + _("Dig a hole") + " → " + _("Cover with soil"),
                    _("Cover with soil") + " → " + _("Put in seed") + " → " + _("Dig a hole")
                ]
            },
        ]
        seq = random.choice(sequences)

        question = f'''
            <p><b>{seq["task"]}</b></p>
            <p>''' + _("Put the steps in the correct order:") + '''</p>
        '''

        options = seq["options"].copy()
        random.shuffle(options)

        return {
            "type": "coding",
            "strand": _("Coding"),
            "q": question,
            "a": seq["correct"],
            "options": options
        }


# Keep the old class name for backwards compatibility
CodingMaze = CodingQuestions
