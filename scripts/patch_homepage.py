with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'Download Offline State Evacuation Map\n              </button>'
replacement = '''Download Offline State Evacuation Map
              </button>'''

# Let's inspect the exact lines around 437
lines = text.splitlines(keepends=True)
for i, line in enumerate(lines):
    if 'Download Offline State Evacuation Map' in line:
        start = max(0, i - 3)
        end = min(len(lines), i + 3)
        print("Found at lines:", start, "to", end)
        for j in range(start, end):
            print(f"{j}: {repr(lines[j])}")

        # Replace button tag
        new_block = [
            '              <button\n',
            '                onClick={async () => {\n',
            '                  try {\n',
            '                    const res = await fetch("http://127.0.0.1:8000/api/v1/bulletins/1.pdf");\n',
            '                    if (!res.ok) { window.location.href = "/bulletin"; return; }\n',
            '                    const blob = await res.blob();\n',
            '                    const url = window.URL.createObjectURL(blob);\n',
            '                    const a = document.createElement("a");\n',
            '                    a.href = url;\n',
            '                    a.download = "Gujarat_State_Evacuation_Map.pdf";\n',
            '                    document.body.appendChild(a);\n',
            '                    a.click();\n',
            '                    window.URL.revokeObjectURL(url);\n',
            '                    document.body.removeChild(a);\n',
            '                  } catch (e) {\n',
            '                    window.location.href = "/bulletin";\n',
            '                  }\n',
            '                }}\n',
            '                className="w-full py-3 px-6 rounded border border-primary/50 bg-surface-container hover:bg-surface-container-high text-primary font-label-code text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer"\n',
            '              >\n',
            '                <span className="material-symbols-outlined text-sm">download_for_offline</span>\n',
            '                Download Offline State Evacuation Map\n',
            '              </button>\n'
        ]
        # Replace the 4 lines around the button
        lines[i-2:i+2] = new_block
        with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'w', encoding='utf-8') as out_f:
            out_f.writelines(lines)
        print("MODIFIED HOMEPAGE SUCCESSFULLY!")
        break

