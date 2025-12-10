import sys

# Define the maximum alphabet size (e.g., 256 for standard ASCII/extended ASCII)
ALPHABET_SIZE = 256

class BoyerMoore:
    """
    Implements the Boyer-Moore string-matching algorithm.
    It combines the Bad Character and Good Suffix heuristics for fast searching.
    """
    def __init__(self, pattern: str):
        """
        Initializes the Boyer-Moore instance by pre-processing the pattern
        to build the shift tables.
        """
        self.pattern = pattern
        self.m = len(pattern)
        # Use ALPHABET_SIZE defined above
        self.bad_char = self._build_bad_char_table()
        self.good_suffix = self._build_good_suffix_table()

    def _build_bad_char_table(self):
        """
        Builds the Bad Character shift table (R array).
        Stores the index of the rightmost occurrence of each character in the pattern.
        """
        table = [-1] * ALPHABET_SIZE
        for i, ch in enumerate(self.pattern):
            # Use ord() to get the ASCII/Unicode value for table indexing
            # Handle characters outside the ASCII range gracefully
            char_code = ord(ch)
            if char_code < ALPHABET_SIZE:
                table[char_code] = i
        return table

    def _build_good_suffix_table(self):
        """
        Builds the Good Suffix shift table (based on the border array).
        This logic is derived from the KMP preprocessing used on the reversed pattern.
        """
        m = self.m
        # Array to hold the shift values
        good_suffix = [0] * (m + 1)
        # Array to hold the border positions (prefix=suffix lengths)
        border_pos = [0] * (m + 1)

        # 1. Calculate the border array for the pattern
        i = m # Index in pattern
        j = m + 1 # Index in border_pos/pattern (shifted)
        border_pos[i] = j

        while i > 0:
            # Find the longest border (matching prefix and suffix)
            while j <= m and self.pattern[i - 1] != self.pattern[j - 1]:
                # Case 2: Mismatch, so the shift for a suffix of length m-i+1 
                # (which ends at position i-1) is defined by a smaller border
                if good_suffix[j] == 0:
                    good_suffix[j] = j - i
                j = border_pos[j]
            i -= 1
            j -= 1
            border_pos[i] = j

        # 2. Fill the rest of the good_suffix table
        # Case 1: Matching a prefix of the pattern
        j = border_pos[0]
        for i in range(m + 1):
            if good_suffix[i] == 0:
                good_suffix[i] = j
            # Update j to the next border for the next iteration
            if i == j:
                j = border_pos[j]

        return good_suffix

    def search(self, text: str) -> list[int]:
        """
        Searches for all occurrences of the pattern in the text.
        Returns a list of starting indices of matches.
        """
        n = len(text)
        m = self.m
        matches = []
        s = 0  # Shift/start index of the pattern window in the text

        if m == 0 or m > n:
            return matches

        while s <= n - m:
            j = m - 1  # Index in the pattern, starting from the right

            # 1. Compare pattern with text window from right to left
            while j >= 0 and self.pattern[j] == text[s + j]:
                j -= 1

            # 2. Match found (j < 0 means the whole pattern matched)
            if j < 0:
                matches.append(s)
                # Shift by the value from the Good Suffix table for a full match (index 0)
                s += self.good_suffix[0]
            else:
                # 3. Mismatch occurred at index j
                mismatch_char_code = ord(text[s + j])
                
                # Bad Character Shift:
                # Default to -1 if character is not in the ASCII range or not in the pattern.
                if mismatch_char_code >= ALPHABET_SIZE:
                     bad_char_idx = -1
                else:
                     bad_char_idx = self.bad_char[mismatch_char_code]

                # Shift needed to align the last occurrence of the mismatch char with j
                bad_char_shift = j - bad_char_idx

                # Good Suffix Shift:
                # j + 1 is the length of the matched suffix (m - 1 - j)
                good_suffix_shift = self.good_suffix[j + 1]

                # Shift by the maximum of 1, Bad Character Shift, and Good Suffix Shift
                s += max(1, max(bad_char_shift, good_suffix_shift))

        return matches

if __name__ == '__main__':
    # Example usage for testing
    text = "ABAABAACABABA"
    pattern = "ABA"
    bm = BoyerMoore(pattern)
    positions = bm.search(text)
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    # Expected: [0, 4, 10]
    print(f"Matches found at: {positions}") 
    
    text2 = "this is a hello world example with hello again"
    pattern2 = "hello"
    bm2 = BoyerMoore(pattern2)
    positions2 = bm2.search(text2)
    print(f"\nText: {text2}")
    print(f"Pattern: {pattern2}")
    # Expected: [10, 34]
    print(f"Matches found at: {positions2}")