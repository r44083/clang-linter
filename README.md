# clang-linter
Sublime text plugin for static C/C++ code analysis

1. Copy "ClangLinter" folder to "./Data/Packages".
2. Reload sublime_text.
3. Add settings for ClangLinetr (should be on clanglinter_cmd_options sectionss) into the *.sublime-project file:
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
4. Make shure that clang.exe folder was added to your PATH variable.
5. Enjoy

Example:

![](https://habrastorage.org/files/98c/a94/ae4/98ca94ae4f8a41918c452c2dce65a96c.png)
