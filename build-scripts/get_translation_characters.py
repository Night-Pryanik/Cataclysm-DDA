#!/usr/bin/env python3

# Use the Unicode Common Locale Data Repository to create code that
# creates ImGui glyph ranges for each locale, so that every locale can
# have properly rendered text.

import itertools
import sys
from cldr_language_helpers import alphabets


def add_preprocessor():
    print("#if defined(__GNUC__) or defined(__clang__)\n"
          "#define NOINLINE __attribute__ ((noinline))\n"
          "#else\n"
          "#define NOINLINE __declspec(noinline)\n"
          "#endif\n"
          "#if defined(__clang__)\n"
          "#define NOUNROLL _Pragma(\"clang loop unroll(disable)\")\n"
          "#elif defined(__GNUC__)\n"
          "#define NOUNROLL #pragma GCC unroll 0\n"
          "#else\n"
          "#define NOUNROLL\n"
          "#endif\n")


def main():
    print("// generated by get_translation_characters.py; example:\n"
          "//   ./build-scripts/get_translation_characters.py en ar cs da de "
          "el es fr hu id is it ja ko nb nl pl pt ru sr tr uk_UA zh_Hans "
          "zh_Hant > src/cldr/imgui-glyph-ranges.cpp\n\n"
          "// NOLINTBEGIN(cata-static-declarations,readability-function-size,"
          "modernize-avoid-c-arrays)\n")
    add_preprocessor()
    print("namespace {\n"
          "NOINLINE void AddGlyphs( ImFontGlyphRangesBuilder *b, "
          "ImWchar const *glyphp, ImWchar const *end) {\n"
          "  NOUNROLL\n"
          "  for( ; glyphp != end; ++glyphp ) {\n"
          "    b->AddChar(*glyphp);\n"
          "  }\n"
          "}\n"
          "} // namespace")
    try:
        for language in sys.argv[1:]:
            print_func(language)
        print("// NOLINTEND(cata-static-declarations,"
              "readability-function-size,modernize-avoid-c-arrays)\n")
        return 0
    except KeyError as x:
        print(f"Unknown language code “{x.args[0]}”", file=sys.stderr)
        return 1


def chunks(xs, n):
    n = max(1, n)
    return (xs[i:i + n] for i in range(0, len(xs), n))


def print_func(language):
    print(f"static void AddGlyphRangesFromCLDRFor{language.upper()}("
          "ImFontGlyphRangesBuilder *b) {")
    # All of the glyphs used this language
    chars = []
    for c in alphabets.ALPHABETS_BY_LANG_MAP[language]:
        for g in c:
            chars.append(ord(g))
    for c in alphabets.ALPHABETS_BY_LANG_MAP[language]:
        for g in c.upper():
            chars.append(ord(g))
    for c in alphabets.NUMBERS_BY_LANG_MAP[language]:
        for g in c:
            chars.append(ord(g))
    for c in alphabets.PUNCTUATION_BY_LANG_MAP[language]:
        for g in c:
            chars.append(ord(g))
    # Sort and remove duplicates, so we can detect sequences
    chars = [hex(c) for c in sorted(list(set(chars)))]

    print("  static constexpr ImWchar glyphs[] = {")
    char_chunks = list(chunks(chars, 16))
    for cs in itertools.islice(char_chunks, len(char_chunks) - 1):
        print(", ".join(cs) + ",")
    print(", ".join(char_chunks[-1]))
    print("  };")
    print("  AddGlyphs(b, glyphs, glyphs + std::extent_v<decltype(glyphs)>);")
    print("}")


if __name__ == '__main__':
    sys.exit(main())
