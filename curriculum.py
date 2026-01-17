import random

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
            question = f"What is {a} + {b}?"
            answer = a + b
            options = [answer, answer + random.randint(1, 3), answer - random.randint(1, 3)]
        else:
            a = random.randint(10, 50)
            b = random.randint(1, a)  # Ensure positive result
            question = f"What is {a} - {b}?"
            answer = a - b
            options = [answer, answer + random.randint(1, 5), answer - random.randint(1, 5)]
        
        # Visual Aid (Emojis) for smaller numbers
        if a <= 10 and b <= 10:
            emoji = random.choice(['🍎', '⭐', '🐸', '🍪'])
            question += f"<br><span style='font-size:2rem'>{' '.join([emoji]*a)} &nbsp;{op}&nbsp; {' '.join([emoji]*b)}</span>"

    # --- STRAND C: ALGEBRA (Patterns & Equalities) ---
    elif strand == 'algebra':
        # Pattern Completion
        patterns = [
            (['🔴', '🔵', '🔴', '🔵'], '🔴'),
            (['🔼', '🔼', '🔽', '🔼', '🔼'], '🔽'),
            (['A', 'B', 'B', 'A', 'B'], 'B')
        ]
        pat, correct = random.choice(patterns)
        display_pat = " ".join(pat) + " ... ?"
        question = f"What comes next in the pattern?<br><br><b>{display_pat}</b>"
        answer = correct
        options = [correct, '❌', '❓'] # Simplified distractors

    # --- STRAND D: DATA (Sorting & Graphs) ---
    elif strand == 'data':
        # Simple Logic: "Which has more?"
        t1, t2 = random.sample(['Cats 🐱', 'Dogs 🐶', 'Birds 🐦'], 2)
        v1, v2 = random.randint(3, 9), random.randint(3, 9)
        while v1 == v2: v2 = random.randint(3, 9) # Ensure not equal
        
        # Generate a mini text-graph
        graph = f"{t1}: { '█' * v1 } ({v1})<br>{t2}: { '█' * v2 } ({v2})"
        question = f"Look at the graph. Which group has <b>more</b>?<br><div class='graph'>{graph}</div>"
        answer = t1 if v1 > v2 else t2
        options = [t1, t2]

    # --- STRAND E: SPATIAL SENSE (Shapes) ---
    elif strand == 'spatial':
        shapes = {
            'Triangle': '🔺',
            'Circle': '🔵',
            'Square': '🟥',
            'Rectangle': '🟩'
        }
        target_name, target_emoji = random.choice(list(shapes.items()))
        question = f"Which one is a <b>{target_name}</b>?"
        answer = target_emoji
        options = list(shapes.values())

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
            question = f"How many <b>tens</b> are in the number {num}?<br><div style='font-size:1.5rem;margin:10px 0'>{blocks_visual.strip()}</div>"
            answer = str(tens)
            options = [str(tens), str(tens + 1) if tens < 5 else str(tens - 1), str(ones)]

        elif mode == 'identify_ones':
            num = random.randint(10, 50)
            tens = num // 10
            ones = num % 10
            blocks_visual = "🟫 " * tens + "🟨 " * ones if ones > 0 else "🟫 " * tens
            question = f"How many <b>ones</b> are in the number {num}?<br><div style='font-size:1.5rem;margin:10px 0'>{blocks_visual.strip()}</div>"
            answer = str(ones)
            options = [str(ones), str(tens), str((ones + 2) % 10)]

        elif mode == 'compose':
            tens = random.randint(1, 4)
            ones = random.randint(0, 9)
            correct = tens * 10 + ones
            question = f"<b>{tens} tens</b> and <b>{ones} ones</b> = ?"
            answer = str(correct)
            options = [str(correct), str(correct + 10), str(correct + 1) if ones < 9 else str(correct - 1)]

        else:  # decompose
            num = random.randint(11, 49)
            tens = num // 10
            ones = num % 10
            question = f"Break apart <b>{num}</b> into tens and ones:"
            answer = f"{tens} tens, {ones} ones"
            options = [
                f"{tens} tens, {ones} ones",
                f"{tens + 1} tens, {ones} ones",
                f"{tens} tens, {ones + 1} ones" if ones < 9 else f"{tens} tens, {ones - 1} ones"
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
            "strand": "Place Value",
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
            question = f"What time does the clock show?{clock_html}"
            answer = f"{hour}:00"
            other_hour = (hour % 12) + 1
            options = [f"{hour}:00", f"{other_hour}:00", f"{hour}:30"]

        elif mode == 'read_half':
            hour = random.randint(1, 12)
            clock_html = self._draw_clock(hour, 30)
            question = f"What time does the clock show?{clock_html}"
            answer = f"{hour}:30"
            other_hour = (hour % 12) + 1
            options = [f"{hour}:30", f"{hour}:00", f"{other_hour}:00"]

        else:  # activity matching
            activities = [
                ("wake up for school", "7:00"),
                ("eat lunch", "12:00"),
                ("eat dinner", "6:00"),
                ("go to bed", "8:00"),
            ]
            activity, time = random.choice(activities)
            question = f"What time do most kids <b>{activity}</b>?"
            answer = time
            all_times = ["7:00", "12:00", "6:00", "8:00", "3:00"]
            options = [t for t in all_times if t != time][:2] + [time]

        random.shuffle(options)
        return {
            "type": "time",
            "strand": "Time",
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
                ("pencil", 5, "✏️"),
                ("crayon", 3, "🖍️"),
                ("marker", 6, "🖊️"),
                ("eraser", 2, "🧽"),
                ("book", 8, "📕"),
            ]
            item1 = random.choice(items)
            item2 = random.choice([i for i in items if i[0] != item1[0]])

            bar1 = "█" * item1[1]
            bar2 = "█" * item2[1]

            question = f'''Which is <b>longer</b>?<br>
            <div style="text-align:left;margin:15px;font-family:monospace;">
                <div>{item1[2]} {item1[0].title()}: <span style="color:#3498db">{bar1}</span></div>
                <div>{item2[2]} {item2[0].title()}: <span style="color:#e74c3c">{bar2}</span></div>
            </div>'''

            if item1[1] > item2[1]:
                answer = item1[0].title()
            else:
                answer = item2[0].title()
            options = [item1[0].title(), item2[0].title(), "They are the same"]

        elif mode == 'count_units':
            units = random.randint(3, 7)
            unit_emoji = random.choice(["📎", "🧱", "📏"])
            line = "━" * (units * 2)

            question = f'''How many {unit_emoji} long is this line?<br>
            <div style="margin:15px 0;font-size:1.5rem;">{line}</div>
            <div style="font-size:1.3rem;">{unit_emoji * units}</div>'''

            answer = str(units)
            options = [str(units), str(units + 1), str(units - 1)]

        else:  # order by size
            question = "Put these in order from <b>shortest to longest</b>:<br><br>🐜 Ant, 🐱 Cat, 🐘 Elephant"
            answer = "Ant, Cat, Elephant"
            options = [
                "Ant, Cat, Elephant",
                "Elephant, Cat, Ant",
                "Cat, Ant, Elephant"
            ]

        random.shuffle(options)
        return {
            "type": "measurement",
            "strand": "Measurement",
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
                ("Sara has {a} 🍎 apples. Mom gives her {b} more. How many apples does Sara have now?", "🍎"),
                ("There are {a} 🐦 birds in a tree. {b} more birds fly in. How many birds are there now?", "🐦"),
                ("Tom has {a} 🍪 cookies. He bakes {b} more. How many cookies does he have?", "🍪"),
                ("You have {a} ⭐ stickers. Your friend gives you {b} more. How many stickers do you have?", "⭐"),
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
                ("You have {a} 🎈 balloons. {b} pop! How many balloons are left?", "🎈"),
                ("There are {a} 🍪 cookies. You eat {b}. How many cookies are left?", "🍪"),
                ("{a} 🐸 frogs are on a log. {b} jump away. How many frogs are still on the log?", "🐸"),
                ("Mom baked {a} 🧁 cupcakes. You ate {b}. How many are left?", "🧁"),
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
            "strand": "Word Problems",
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

            question = f"Which number is <b>greater</b>?<br><div style='font-size:2.5rem;margin:15px 0;'>{a} &nbsp;&nbsp; or &nbsp;&nbsp; {b}</div>"
            answer = str(max(a, b))
            options = [str(a), str(b), "They are equal"]

        elif mode == 'fill_symbol':
            a = random.randint(1, 30)
            b = random.randint(1, 30)

            question = f"Fill in the blank:<br><div style='font-size:2.5rem;margin:15px 0;'>{a} &nbsp; ⬜ &nbsp; {b}</div><p>Choose the correct symbol:</p>"

            if a > b:
                answer = ">"
            elif a < b:
                answer = "<"
            else:
                answer = "="
            options = [">", "<", "="]

        else:  # number_line
            target = random.randint(5, 15)
            question = f'''Look at the number line. Which number is <b>greater than {target}</b>?<br>
            <div style="margin:15px 0;font-family:monospace;">
                ◀─ {target-3} ─ {target-2} ─ {target-1} ─ <b>{target}</b> ─ {target+1} ─ {target+2} ─ {target+3} ─▶
            </div>'''
            answer = str(target + random.randint(1, 3))
            wrong1 = str(target - random.randint(1, 2))
            wrong2 = str(target)
            options = [answer, wrong1, wrong2]

        random.shuffle(options)
        return {
            "type": "comparing",
            "strand": "Comparing",
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

            question = f"Count by <b>{skip}s</b>. What comes next?<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
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

            question = f"Count by <b>{skip}s</b>. What is the missing number?<br><div style='font-size:1.8rem;margin:15px 0;'>{display}</div>"
            answer = str(missing)
            options = [str(missing), str(missing + 1), str(missing - 1)]

        else:  # count_objects
            count = random.randint(3, 6)
            if skip == 2:
                emoji = "👟"
                item = "pairs of shoes"
            elif skip == 5:
                emoji = "🖐️"
                item = "hands (5 fingers each)"
            else:  # 10
                emoji = "🔟"
                item = "groups of 10"

            total = count * skip
            question = f"Count by <b>{skip}s</b>. How many in total?<br><div style='font-size:2rem;margin:15px 0;'>{emoji * count}</div><p>{count} {item}</p>"
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
            "strand": "Skip Counting",
            "q": question,
            "a": answer,
            "options": unique
        }


class MoneyCounting:
    def __init__(self):
        # Canadian Coins: (Value in cents, CSS Class, Label for Accessibility)
        self.coins = [
            {"val": 5,   "css": "nickel",   "name": "Nickel"},
            {"val": 10,  "css": "dime",     "name": "Dime"},
            {"val": 25,  "css": "quarter",  "name": "Quarter"},
            {"val": 100, "css": "loonie",   "name": "Loonie ($1)"},
            {"val": 200, "css": "toonie",   "name": "Toonie ($2)"}
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
                <br>What is this coin?"""
            
            answer = target['name']
            # Distractors: Other coin names
            options = [c['name'] for c in self.coins if c['name'] != answer]
            random.shuffle(options)
            options = options[:2] + [answer]
            random.shuffle(options)
            
            return {
                "type": "financial",
                "strand": "Financial",
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
            
            question_html = f"How much money is this?<br><div class='coin-container'>{coins_html}</div>"
            
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
                "strand": "Financial",
                "q": question_html,
                "a": answer_str,
                "options": options
            }


class CodingMaze:
    def __init__(self):
        self.grid_size = 3  # Keep it small for Grade 1 (3x3)
        self.moves = {
            '⬆️': (-1, 0),
            '⬇️': (1, 0),
            '⬅️': (0, -1),
            '➡️': (0, 1)
        }

    def generate(self):
        """Generates a 'Get the Robot to the Star' puzzle."""
        
        # 1. Place Robot and Star (Start & End)
        # We use simple (row, col) coordinates
        cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        start, end = random.sample(cells, 2)
        
        # 2. Calculate the Correct Path (The "Algorithm")
        # For Grade 1, we want the simplest path (Manhattan distance)
        path = []
        curr_r, curr_c = start
        target_r, target_c = end
        
        # Move Vertically
        while curr_r != target_r:
            if target_r > curr_r:
                path.append('⬇️')
                curr_r += 1
            else:
                path.append('⬆️')
                curr_r -= 1
                
        # Move Horizontally
        while curr_c != target_c:
            if target_c > curr_c:
                path.append('➡️')
                curr_c += 1
            else:
                path.append('⬅️')
                curr_c -= 1
        
        # 3. Generate "Buggy" Code (Wrong Options)
        correct_code = " ".join(path)
        options = set()
        options.add(correct_code)
        
        while len(options) < 3:
            # Create mutations (wrong directions, extra steps, missing steps)
            fake_path = path.copy()
            if len(fake_path) > 1:
                random.shuffle(fake_path) # Wrong order
            else:
                fake_path.append(random.choice(list(self.moves.keys()))) # Extra step
            
            fake_str = " ".join(fake_path)
            if fake_str != correct_code:
                options.add(fake_str)

        # 4. Render the Grid (ASCII/HTML)
        # We render a table to send to the frontend
        grid_html = "<table class='maze-grid'>"
        for r in range(self.grid_size):
            grid_html += "<tr>"
            for c in range(self.grid_size):
                cell_content = "⬜" # Empty
                if (r, c) == start:
                    cell_content = "🤖"
                elif (r, c) == end:
                    cell_content = "⭐"
                
                grid_html += f"<td>{cell_content}</td>"
            grid_html += "</tr>"
        grid_html += "</table>"

        return {
            "type": "coding",
            "strand": "Coding",
            "q": f"Which code gets the Robot to the Star?<br>{grid_html}",
            "a": correct_code,
            "options": list(options)
        }