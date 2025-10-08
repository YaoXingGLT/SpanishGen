#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import random
import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class PhonologySystem:
    """音韻系統"""
    consonants: Set[str] = field(default_factory=lambda: {'p', 'b', 't', 'd', 'k', 'g', 'm', 'n', 's', 'z', 'l', 'r', 'ñ','ll','j', 'ch', 'f', 'v', 'h'})
    vowels: Set[str] = field(default_factory=lambda: {'a', 'e', 'i', 'o', 'u'})
    syllable_patterns: List[str] = field(default_factory=lambda: [
    'CV',   
    'CVC',    
    'CVV',   
    'V', 
    'CCV'  
])
    phonotactic_rules: List[str] = field(default_factory=list)
    


    def generate_syllable(self) -> str:
        ALLOWED_CLUSTERS = [
        'pl', 'pr', 'bl', 'br', 'fl', 'fr', 
        'cl', 'cr', 'gl', 'gr', 
        'tr', 'dr'
        ]
        pattern = random.choice(self.syllable_patterns)
        syllable = ""
        
        if pattern == 'CCV':
            cluster = random.choice(ALLOWED_CLUSTERS)
            vowel = random.choice(list(self.vowels))
            syllable = cluster + vowel

        else:
            for char in pattern:
                if char == 'C':
                    syllable += random.choice(list(self.consonants))
                elif char == 'V':
                    syllable += random.choice(list(self.vowels))

        return syllable

    def generate_word(self, syllable_count: int = None) -> str:
        """生成詞語，並檢查音韻合法性（避免非法 cluster、過長母音、非法詞尾）"""
        ALLOWED_CLUSTERS = [
            'pl', 'pr', 'bl', 'br', 'fl', 'fr',
            'cl', 'cr', 'gl', 'gr',
            'tr', 'dr'
        ]
        ALLOWED_FINAL_CONSONANTS = {'n', 's', 'r', 'l', 'd', 'z'}

        if syllable_count is None:
            syllable_count = random.randint(1, 3)

        while True:
            # === 1️⃣ 生成基本音節 ===
            word = ""
            for _ in range(syllable_count):
                word += self.generate_syllable()

            # 🚫 開頭不能是 "rr"
            if word.startswith("rr"):
                continue

            regenerate = False

            # === 2️⃣ 避免非法子音群 ===
            clusters = re.findall(r'[^aeiou]{2}', word)
            for c in clusters:
                if c not in ALLOWED_CLUSTERS:
                    regenerate = True
                    break

            # === 3️⃣ 避免三連以上母音 ===
            if re.search(r'[aeiou]{3,}', word):
                regenerate = True

            # === 4️⃣ 避免非法詞尾 ===
            if re.search(r'[^aeiou]$', word):  # 以子音結尾
                last = word[-1]
                if last not in ALLOWED_FINAL_CONSONANTS:
                    regenerate = True

            # 若都合法 → 返回詞語
            if not regenerate:
                return word

@dataclass
class MorphologyRule:
    """構詞規則"""
    name: str
    rule_type: str  # prefix, suffix, infix, reduplication
    marker: str
    meaning: str
    position: str = ""

@dataclass
class MorphologySystem:
    """構詞系統"""
    rules: List[MorphologyRule] = field(default_factory=list)
    word_classes: Dict[str, List[str]] = field(default_factory=lambda: {
        'noun': [], 'verb': [], 'adjective': [], 'adverb': []
    })

    def add_rule(self, name: str, rule_type: str, marker: str, meaning: str):
        """添加構詞規則"""
        rule = MorphologyRule(name, rule_type, marker, meaning)
        self.rules.append(rule)

    def apply_morphology(self, base_word: str, rule_name: str) -> str:
        """應用構詞規則"""
        for rule in self.rules:
            if rule.name == rule_name:
        # ✅ 特別處理複數
                if rule_name == "plural":
                    return self._apply_plural_rule(base_word)
                if rule.rule_type == 'prefix':
                    return rule.marker + base_word
                elif rule.rule_type == 'suffix':
                    return base_word + rule.marker
                elif rule.rule_type == 'reduplication':
                    return base_word + base_word
        return base_word
    
    def _apply_plural_rule(self, word: str) -> str:
        """根據西班牙語拼寫規則產生複數形"""
        if not word:
            return word

        last = word[-1]

        # 1️⃣ 母音結尾 → +s
        if last in ['a', 'e', 'i', 'o', 'u']:
            return word + 's'

        # 2️⃣ 以 z 結尾 → z → c + es
        if last == 'z':
            return word[:-1] + 'ces'

        # 3️⃣ 其他子音結尾 → +es
        return word + 'es'

@dataclass
class SyntaxRule:
    """句法規則"""
    name: str
    pattern: str  # SVO, SOV, VSO etc.
    description: str

@dataclass
class SyntaxSystem:
    """句法系統"""
    word_order: str = "SVO"
    rules: List[SyntaxRule] = field(default_factory=list)

    def add_rule(self, name: str, pattern: str, description: str):
        """添加句法規則"""
        rule = SyntaxRule(name, pattern, description)
        self.rules.append(rule)

    def generate_sentence(self, subject: str, verb: str, obj: str = "") -> str:
        """根據語序生成句子"""
        if self.word_order == "SVO":
            return f"{subject} {verb} {obj}".strip()
        elif self.word_order == "SOV":
            return f"{subject} {obj} {verb}".strip()
        elif self.word_order == "VSO":
            return f"{verb} {subject} {obj}".strip()
        else:
            return f"{subject} {verb} {obj}".strip()
    def generate_yesno_question(self, subject: str, verb: str, obj: str = "") -> str:
        """生成西班牙語的是非疑問句"""
        base_sentence = self.generate_sentence(subject, verb, obj)
        return f"¿{base_sentence}?"

class LanguageCreatorGame:
    """語言創造者遊戲主類"""

    def __init__(self):
        self.phonology = PhonologySystem()
        self.morphology = MorphologySystem()
        self.syntax = SyntaxSystem()
        self.vocabulary = defaultdict(list)  # {詞性: [詞語列表]}
        self.current_level = 1


    def display_welcome(self):
        """顯示歡迎訊息"""
        print("=" * 60)
        print("🌍 歡迎來到語言創造者遊戲！ 🌍")
        print("=" * 60)
        print("你將通過三個層次來創造一個全新的語言：")
        print("第一層：音韻系統 (Phonology)")
        print("第二層：構詞系統 (Morphology)")
        print("第三層：句法系統 (Syntax)")
        print("=" * 60)

    def level_1_phonology(self):
        """第一關：設定音韻系統"""
        print("\n🔤 第一關：音韻系統設定")
        print("-" * 40)
        print("讓我們為你的語言設定基本的聲音系統！")

        # 設定子音
        #print(f"\n目前的子音：{', '.join(sorted(self.phonology.consonants))}")
        while True:
            print(f"\n目前的子音：{', '.join(sorted(self.phonology.consonants))}")
            choice = input("\n你想要 (a)添加子音 (b)移除子音 (c)繼續下一步？ ").lower()
            if choice == 'a':
                new_consonant = input("請輸入要添加的子音：")
                if new_consonant and len(new_consonant) <= 2:
                    self.phonology.consonants.add(new_consonant)
                    print(f"已添加子音：{new_consonant}")
            elif choice == 'b':
                remove_consonant = input("請輸入要移除的子音：")
                if remove_consonant in self.phonology.consonants:
                    self.phonology.consonants.remove(remove_consonant)
                    print(f"已移除子音：{remove_consonant}")
            elif choice == 'c':
                break

        # 設定母音
        #print(f"\n目前的母音：{', '.join(sorted(self.phonology.vowels))}")
        while True:
            print(f"\n目前的母音：{', '.join(sorted(self.phonology.vowels))}")
            choice = input("\n你想要 (a)添加母音 (b)移除母音 (c)繼續下一步？ ").lower()

            if choice == 'a':
                new_vowel = input("請輸入要添加的母音：")
                if new_vowel and len(new_vowel) <= 3:
                    self.phonology.vowels.add(new_vowel)
                    print(f"已添加母音：{new_vowel}")

            elif choice == 'b':
                remove_vowel = input("請輸入要移除的母音：")
                if remove_vowel in self.phonology.vowels:
                    self.phonology.vowels.remove(remove_vowel)
                    print(f"已移除母音：{remove_vowel}")
            elif choice == 'c':
                break

        # 設定音節結構
        print(f"\n目前的詞彙音節結構：{', '.join(self.phonology.syllable_patterns)}")
        print("(C=子音, V=母音)")

        # 生成範例詞語
        print("\n🎲 讓我們用你的音韻系統生成一些詞語：")
        for i in range(15):
            word = self.phonology.generate_word()
            print(f"{i+1}. {word}")
            self.vocabulary['unknown'].append(word)

        print(f"\n✅ 第一關完成！")
        self.current_level = 2

    def level_2_morphology(self):
        """第二關：設定構詞系統"""
        print("\n🔧 第二關：構詞系統設定")
        print("-" * 40)
        print("現在我們來為語言添加構詞規則！")

        # 將之前生成的詞語分類
        print("\n首先，讓我們為之前生成的詞語分類：")
        for word in self.vocabulary['unknown'][:]:
            print(f"\n詞語：{word}")
            word_class = input("這個詞是 (n)名詞 (v)動詞 (a)形容詞 (d)副詞？ ").lower()

            if word_class == 'n':
                self.vocabulary['noun'].append(word)
            elif word_class == 'v':
                self.vocabulary['verb'].append(word)
            elif word_class == 'a':
                self.vocabulary['adjective'].append(word)
            elif word_class == 'd':
                self.vocabulary['adverb'].append(word)
            else:
                self.vocabulary['noun'].append(word)  # 預設為名詞

            self.vocabulary['unknown'].remove(word)

        # 添加構詞規則
        print("\n現在我們來創建構詞規則：")

        # 前綴
        self.morphology.add_rule("re_prefix", "prefix", "re", "再次")
        self.morphology.add_rule("des_prefix", "prefix", "des", "否定／反向")
        self.morphology.add_rule("in_prefix", "prefix", "in", "否定")
        self.morphology.add_rule("con_prefix", "prefix", "con", "共同")

        # 後綴
        self.morphology.add_rule("plural_s", "suffix", "s", "複數（母音結尾）")
        self.morphology.add_rule("plural_es", "suffix", "es", "複數（子音結尾）")
        self.morphology.add_rule("cion_suffix", "suffix", "ción", "動作名詞化")
        self.morphology.add_rule("mente_suffix", "suffix", "mente", "副詞化")
        self.morphology.add_rule("ar_suffix", "suffix", "ar", "動詞不定式")
        self.morphology.add_rule("er_suffix", "suffix", "er", "動詞不定式")
        self.morphology.add_rule("ir_suffix", "suffix", "ir", "動詞不定式")
        self.morphology.add_rule("plural", "suffix", "", "自動判斷複數")



        print(f"\n✅ 第二關完成！")
        self.current_level = 3

    def level_3_syntax(self):
        """第三關：設定句法系統"""
        print("\n📝 第三關：句法系統設定")
        print("-" * 40)
        print("最後，我們來設定語言的句子結構！")

        # 設定基本語序
        print("\n請選擇基本語序：")
        print("1. SVO (主語-動詞-賓語) - 如英文、中文")
        print("2. SOV (主語-賓語-動詞) - 如日文、韓文")
        print("3. VSO (動詞-主語-賓語) - 如愛爾蘭語、南島語")

        order_choice = input("請選擇 (1-3)：") or "1"

        if order_choice == "1":
            self.syntax.word_order = "SVO"
        elif order_choice == "2":
            self.syntax.word_order = "SOV"
        elif order_choice == "3":
            self.syntax.word_order = "VSO"

        print(f"已設定語序：{self.syntax.word_order}")

        # 添加句法規則
        self.syntax.add_rule("basic_sentence", self.syntax.word_order, "基本句型")

        # 疑問句規則
        question_marker = input("請設定疑問標記（預設為 '¿?'）：") or "¿?"
        self.syntax.add_rule("question", f"{self.syntax.word_order}+{question_marker}", "疑問句")

        # 生成範例句子
        print(f"\n🎨 讓我們用 {self.syntax.word_order} 語序生成一些句子：")

        # 確保各詞類都有詞語
        if not self.vocabulary['noun']:
            self.vocabulary['noun'].append(self.phonology.generate_word())
        if not self.vocabulary['verb']:
            self.vocabulary['verb'].append(self.phonology.generate_word())

        for i in range(3):
            subject = random.choice(self.vocabulary['noun'])
            verb = random.choice(self.vocabulary['verb'])
            obj = random.choice(self.vocabulary['noun']) if len(self.vocabulary['noun']) > 1 else ""

            sentence = self.syntax.generate_sentence(subject, verb, obj)
            print(f"{i+1}. {sentence}")

            # 疑問句版本
            question_sentence = f"¿{sentence}?"
            print(f"   疑問句：{question_sentence}")

        print(f"\n✅ 第三關完成！")

    def final_showcase(self):
        """最終展示創造的語言"""
        print("\n" + "=" * 60)
        print("🎉 恭喜！你已經成功創造了一個新語言！ 🎉")
        print("=" * 60)


        print(f"\n🔤 音韻系統:")
        print(f"   子音：{', '.join(sorted(self.phonology.consonants))}")
        print(f"   母音：{', '.join(sorted(self.phonology.vowels))}")
        print(f"   音節模式：{', '.join(self.phonology.syllable_patterns)}")

        print(f"\n🔧 構詞系統:")
        for rule in self.morphology.rules:
            print(f"   {rule.name}: {rule.rule_type} '{rule.marker}' ({rule.meaning})")

        print(f"\n📝 句法系統:")
        print(f"   基本語序：{self.syntax.word_order}")
        for rule in self.syntax.rules:
            print(f"   {rule.name}: {rule.pattern}")

        print(f"\n📚 詞彙統計:")
        for word_class, words in self.vocabulary.items():
            if words and word_class != 'unknown':
                print(f"   {word_class}: {len(words)} 個詞")

        # ✅ 改進版：最終語言展示
        print(f"\n🌟 你的語言作品展示:")

        for i in range(6):
            if self.vocabulary['noun'] and self.vocabulary['verb']:
                # === 1️⃣ 選取詞彙 ===
                subject = random.choice(self.vocabulary['noun'])
                verb = random.choice(self.vocabulary['verb'])
                obj = random.choice(self.vocabulary['noun']) if len(self.vocabulary['noun']) > 1 else ""

                # === 2️⃣ 套用構詞規則 ===
                # 名詞 → 複數
                if random.random() < 0.3:  # 30% 機率複數化主語
                    subject = self.morphology.apply_morphology(subject, "plural")
                if obj and random.random() < 0.3:
                    obj = self.morphology.apply_morphology(obj, "plural")

                # 動詞 → 否定 / 不定式 / 時態變化（可視情況擴充）
                if random.random() < 0.3:
                    verb = self.morphology.apply_morphology(verb, "in_prefix")
                elif random.random() < 0.3:
                    verb = self.morphology.apply_morphology(verb, "ar_suffix")

                # 副詞 → -mente（如有形容詞可改 obj）
                if self.vocabulary['adjective'] and random.random() < 0.3:
                    adj = random.choice(self.vocabulary['adjective'])
                    adv = self.morphology.apply_morphology(adj, "mente_suffix")
                    obj = f"{adv} {obj}"

                # === 3️⃣ 生成句子 ===
                if random.random() < 0.2:
                    sentence = self.syntax.generate_yesno_question(subject, verb, obj)
                else:
                    sentence = self.syntax.generate_sentence(subject, verb, obj)

                print(f"   {sentence}")

    def run_game(self):
        """運行遊戲主循環"""
        self.display_welcome()

        input("\n按 Enter 開始遊戲...")

        # 第一關：音韻
        if self.current_level == 1:
            self.level_1_phonology()

        # 第二關：構詞
        if self.current_level == 2:
            input("\n按 Enter 進入第二關...")
            self.level_2_morphology()

        # 第三關：句法
        if self.current_level == 3:
            input("\n按 Enter 進入第三關...")
            self.level_3_syntax()

        # 最終展示
        input("\n按 Enter 查看你創造的語言...")
        self.final_showcase()

def main():
    """主程式"""
    game = LanguageCreatorGame()
    game.run_game()

if __name__ == "__main__":
    main()
