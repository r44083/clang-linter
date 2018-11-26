# clang-linter
Sublime text plugin for static C/C++ code analysis

### How to use:

1. Copy ClangLinter folder to "sublime_text/Data/Packages".
2. Reload sublime_text.
3. Add some project-specific settings for ClangLinter into clanglinter_cmd_options sections in the *.sublime-project file:
```
{
	"settings":
	{
		"clanglinter_cmd_options":
		[
			"-I${project_path}/src",
			
			"-DSTM32F40_41xxx",
			"-DHSE_VALUE=8000000",
			"-DARM_MATH_CM4",
			"-std=gnu99",
			"-Wall",
			"-fsyntax-only",
			"-Wunused-macros",
			//"-Weverything",
			"-Wno-parentheses",
		]
	}
}
```
4. Make shure that clang.exe is available from your PATH variable.
5. Enjoy

Example:
--------
![](https://habrastorage.org/files/98c/a94/ae4/98ca94ae4f8a41918c452c2dce65a96c.png)

### TODO
- [ ] Fix bug: you will get the error in the end of analysing some file in case if you switch to another view during the analyzing (ClangContext is too late)

- [ ] Fix bug: if you switch from the analyzed file to the tab with the unsaved file (without a name and path, for example some unsaved file) - the output_panel is not automatically hidden

- [ ] Add code analysis "on the fly" (analyze the code at the time of writing)

- [ ] Add an option to the settings: show output_panel only after saving the file

- [ ] Add recursive search of source code in child folders

- [ ] Add the ability to exclude specified files from the analyzing

- [ ] When automatically switching to a column in the edited file from "output_panel", automatically determine the size of the tabulation and adjust the cursor position according to tab size. Also consider whether there is a tab character at all, and their number to the required column

- [ ] Add the ability to copy (by Ctrl + C) error text from "output_panel"

- [ ] Add mechanism to set cursor to the "problematic" plase when  switching to file. Row and column in the "output_panel" should be checked and the focus in the "output_panel" is automatically set to the row from which the transition was made to this file. Similarly, when returning to the "parent" file (from which the transition was made). (so that the plugin should "remember" the position of the cursor in "output_panel")

- [ ] Add error handling to the parser: clang.exe: error: unknown argument: '-some argument'

- [ ] Add error handling to the parser: fatal error: too many errors emitted, stopping now [-ferror-limit=]

- [ ] Add error handling to the parser: ... 20 errors generated.

- [ ] Add error handling to the parser: clang.exe: error: no input files
