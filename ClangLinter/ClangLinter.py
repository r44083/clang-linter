
import sublime
import sublime_plugin
import subprocess
import os
import re

import tempfile
import codecs

import threading


def plugin_loaded():
	settings.update()

def start_thread(view):
	clanglinter_thread = ClanglinterThread()
	clanglinter_thread.start()
	
	# This is the second case: (but it also doesn't work)
	#sublime.set_timeout_async(AsyncClanglinter.clang_thread(self, edit), 0)

# The code below is for 2nd case (using sublime.set_timeout_async), but is doesn't work
#class AsyncClanglinter():
#   def clang_thread(self, edit):
#       settings.update()
#       if settings.get('enable'):
#           context.update()
#           analyzed_file_content = utils.get_view_content(context.get('view'))
#           temp_file_object = utils.create_temp_file()
#           utils.write_temp_file(temp_file_object, analyzed_file_content)
#          
#           cmd = utils.get_full_cmd(settings.get('clanglinter_cmd'),
#                                   temp_file_object.name,
#                                   settings.get('project_settings'))
#          
#           clang_output = utils.clang_launch(cmd)
#          
#           parser.update(clang_output)
#           parser_output = parser.get_format_output()
#          
#           ui.regions_clear()
#           if parser_output:
#               ui.regions_create()
#               ui.output_panel_clear(edit)
#               ui.output_panel_insert_lines(edit, parser_output)
#               ui.output_panel_show()
#           else:
#               ui.output_panel_clear(edit)
#               ui.output_panel_hide()


class ClanglinterThread(threading.Thread):
	def run(self):
		settings.update()
		if settings.get('enable'):
			context.update()
			last_group_id = context.get('group')
			analyzed_file_content = utils.get_view_content(context.get('view'))
			temp_file_object = utils.create_temp_file()
			utils.write_temp_file(temp_file_object, analyzed_file_content)
			
			cmd = utils.get_full_cmd(settings.get('clanglinter_cmd'),
									temp_file_object.name,
									settings.get('project_settings'))
			
			clang_output = utils.clang_launch(cmd)
			
			parser.update(clang_output)
			parser_output = parser.get_format_output()
			
			context.update()
			
			if(last_group_id is context.get('group')):
				ui.regions_clear()
				if parser_output:
					ui.regions_create()
					sublime.active_window().run_command('output_panel_clear')
					sublime.active_window().run_command('output_panel_insert_lines', {'chars': parser_output})
					ui.output_panel_show()
				else:
					sublime.active_window().run_command('output_panel_clear')
					ui.output_panel_hide()


class OutputPanelClearCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.create_output_panel("clanglinter_panel")
		
		#view.set_read_only(False)
		view.run_command('select_all')
		view.run_command('left_delete')
		#view.set_read_only(True)


class OutputPanelInsertLinesCommand(sublime_plugin.WindowCommand):
	def run(self, **kwargs):
		parser_output = kwargs['chars']
		
		view = self.window.create_output_panel("clanglinter_panel")
		view.set_name('clanglinter_panel')
		
		#self.output_panel_view = view
		
		view.settings().set("line_numbers", True)
		view.settings().set("gutter", True)
		view.settings().set("word_wrap", False)
		view.settings().set("scroll_past_end", False)
		view.settings().set("highlight_line", True)
		#view.settings().set("ruler", False)
		#view.settings().set("result_file_regex",
		#						"^(^\S.*\.\w+):(\d+):(\d+): (\w+ ?\w+?): (.*)$")
		
		#view.settings().set("color_scheme",
		#						"Packages/ClangLinter/ClangLinter_output_panel.hidden-tmTheme")
		
		view.set_syntax_file(
			"Packages/ClangLinter/ClangLinter_output_panel.hidden-tmLanguage")
		
		view.set_read_only(False)
		view.run_command('append', {'characters': parser_output})
		
		# Set cursor on the last line, so on_selection_modified_async() will
		# not be called when we don't want
		view.run_command('goto_line', {"line": 0})
		
		# Scroll output panel to first line without staying cursor on it
		view.show(0)
		
		view.set_read_only(True)


class ClanglinterSettings():
	def update(self):
		window = sublime.active_window()
		view = sublime.active_window().active_view()
		
		all_settings = {}
		
		plugin_settings = sublime.load_settings("ClangLinter.sublime-settings")
		
		all_settings['enable'] = plugin_settings.get('enable')
		all_settings['debug'] = plugin_settings.get('debug')
		
		all_settings['analyze_on_save_only'] = (
			plugin_settings.get('analyze_on_save_only'))
		
		all_settings['show_output_panel'] = (
			plugin_settings.get('show_output_panel'))
		
		all_settings['clanglinter_extensions'] = (
			plugin_settings.get('clanglinter_extensions'))
		
		all_settings['clanglinter_syntaxes'] = (
			plugin_settings.get('clanglinter_syntaxes'))
		
		all_settings['clanglinter_cmd'] = (
			plugin_settings.get('clanglinter_cmd'))
		
		all_settings['project_settings'] = self.__get_project_settings()
		
		self.all_settings = all_settings
	
	def get(self, setting_name):
		if setting_name in self.all_settings:
			return self.all_settings[setting_name]
		else:
			if self.all_settings['debug']:
				print('ClangLinter debug. Settings ERROR:', self.all_settings)
			return None
	
	def __get_project_settings(self):
		# try if any project is open, except - no project is open
		try:
			project_data = sublime.active_window().project_data()
			project_file_name = sublime.active_window().project_file_name()
			
			project_settings = (
					project_data['settings']['clanglinter_cmd_options'])
			
			project_path = os.path.dirname(project_file_name)
			
			for i in range(len(project_settings)):
				project_settings[i] = project_settings[i].replace(
					'${project_path}', project_path)
				# project_settings[i] = project_settings[i].replace("\\", "/")
		except:
			project_settings = []
		
		return project_settings


class ClanglinterContext():
	def __init__(self):
		self.all_context = {}
	
	def update(self):
		window = sublime.active_window()
		view = sublime.active_window().active_view()
		
		all_context = {}
		
		all_context['view'] = view
		all_context['window'] = window.id()
		all_context['group'] = window.active_group()
		all_context['syntax'] = view.settings().get('syntax')
		#all_context['encoding'] = view.encoding()
		
		try:
			all_context['path_basename_extension'] = view.file_name()
		except:
			all_context['path_basename_extension'] = ''
		
		try:
			all_context['path'] = os.path.dirname(all_context['path_basename_extension'])
		except:
			all_context['path'] = ''
		
		try:
			all_context['basename'] = os.path.basename(all_context['path_basename_extension'])
		except:
			all_context['basename'] = ''
		
		try:
			all_context['extension'] = os.path.splitext(all_context['path_basename_extension'])[1][1:]
		except:
			all_context['extension'] = ''
		
		if tempfile.gettempdir():
			temp_dir_path = tempfile.gettempdir() + "\\Clanglinter\\"
			if os.path.isdir(temp_dir_path) == False:
				os.mkdir(temp_dir_path)
			all_context['temp_dir_path'] = temp_dir_path
		else:
			all_context['temp_dir_path'] = ''
		
		self.all_context = all_context
	
	def get(self, context_name):
		if context_name in self.all_context:
			return self.all_context[context_name]


class ClanglinterUtils():
	def clang_launch(self, cmd):
		utils.print_debug("Clang cmd:", cmd)
		
		clang_process = subprocess.Popen(
			cmd,
			# cwd=,
			bufsize=-1,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			shell=True,
			universal_newlines=True)
		
		# output_errors, output_info = p.communicate()
		output_errors = clang_process.stderr.read()
		output_info = clang_process.stdout.read()
		
		utils.print_debug("Clang output:\n", output_errors + output_info)
		return output_errors + output_info
	
	def check_extension(self, file_extension):
		if file_extension in settings.get('clanglinter_extensions'):
			return True
		else:
			utils.print_debug(
				'This file does not satisfy the extension. Current extension',
				file_extension)
			return False
	
	def check_syntax(self, active_view):
		syntax_full_name = active_view.settings().get('syntax')
		syntax_basename = os.path.basename(syntax_full_name)
		
		if syntax_basename in settings.get('clanglinter_syntaxes'):
			return True
		else:
			utils.print_debug(
				'This file does not satisfy the syntax. Current syntax:',
				syntax_basename)
			return False
	
	def create_temp_file(self):
		window = sublime.active_window()
		
		temp_file_basename = "temp_%s" % window.id()
		temp_file_extension = context.get('extension')
		
		#file_object = codecs.open(context.get('temp_dir_path') + \
		#							temp_file_basename + '.' + \
		#							temp_file_extension, 'w+', 'utf-8-sig')
		
		file_object = open(context.get('temp_dir_path') + \
							temp_file_basename + '.' + \
							temp_file_extension, 'w')
		
		return file_object
	
	#def read_file(self, file_full_name):
	#	file_object = open(file_full_name, 'r', encoding="utf8")
	#	return file_object.read()

	def get_view_content(self, active_view):
		return active_view.substr(sublime.Region(0, active_view.size()))
	
	def write_temp_file(self, file_object, string):
		string.encode('utf-8')
		file_object.write(string)
		file_object.close()
	
	def get_full_cmd(self, clanglinter_cmd, temp_file_object_full_name, project_settings):
		
		clanglinter_cmd.append(temp_file_object_full_name)
		
		for option in project_settings:
			clanglinter_cmd.append(option)
		
		return clanglinter_cmd
	
	def print_debug(self, part_1, part_2=''):
		if settings.get('debug'):
			print("ClangLinter debug.", part_1, part_2)


class ClanglinterParser():
	def update(self, input):
		format_output = ''
		parameters_list = []
		
		for line in range(len(input.split('\n'))):
			temp_line = input.split('\n')[line]
			
			parameters = {}
			regex = re.search(
				r'^(^\S.*\.\w+):(\d+):(\d+): (\w+ ?\w+?): (.*)$', temp_line)
			
			if regex is not None:
				parameters['file'] = regex.group(1)
				
				# replace temp file to context file
				if context.get('temp_dir_path') in parameters['file']:
					parameters['file'] = context.get('path_basename_extension')
				
				parameters['line'] = regex.group(2)
				parameters['column'] = regex.group(3)
				parameters['flag'] = regex.group(4)
				parameters['description'] = regex.group(5)
				
				format_output += \
					parameters['file'] + '  ' \
					+ parameters['line'] + ':' \
					+ parameters['column'] + '  ' \
					+ parameters['flag'] + ': ' \
					+ parameters['description'] + '\n'
				
				parameters['line'] = int(parameters['line'])
				parameters['column'] = int(parameters['column'])
				
				parameters_list.append(parameters)
				
		self.format_output = format_output
		self.parameters_list = parameters_list
	
	def get_parameters(self):
		return self.parameters_list
	
	def get_format_output(self):
		return self.format_output
	
	#def get_true_column(self, view, line, column):
	#	tab_size = view.settings().get('tab_size')
	#	
	#	point = view.text_point(line - 1, column - 1)
	#	print('POINT:', point)
	#	line_region = view.line(point)
	#	print('line_region')
	#	raw_line = view.substr(line_region)
	#	print('RAW LINE:', raw_line)
	#	
	#	parser.get_true_column(view, line, column)
	#	point = view.text_point(line, column)
	#	view.sel().clear()
	#	view.sel().add(sublime.Region(10))
	#	print(point)
	
	#def get_true_encoding_name(self, input_encoding_name):
	#	possible_encoding_names = {'UTF-8': 'utf-8', 'UTF-16 LE': ''}


class UserInterface():
	def output_panel_insert_lines(self, edit, parser_output):
		window = sublime.active_window()
		view = window.create_output_panel("clanglinter_panel")
		view.set_name('clanglinter_panel')
		
		#self.output_panel_view = view
		
		view.settings().set("line_numbers", True)
		view.settings().set("gutter", True)
		view.settings().set("word_wrap", False)
		view.settings().set("scroll_past_end", False)
		view.settings().set("highlight_line", True)
		#self.view.settings().set("ruler", False)
		#self.view.settings().set("result_file_regex",
		#						"^(^\S.*\.\w+):(\d+):(\d+): (\w+ ?\w+?): (.*)$")
		
		#self.view.settings().set("color_scheme",
		#						"Packages/ClangLinter/ClangLinter_output_panel.hidden-tmTheme")
		
		view.set_syntax_file(
			"Packages/ClangLinter/ClangLinter_output_panel.hidden-tmLanguage")
		
		view.set_read_only(False)
		view.insert(edit, view.size(), parser_output)
		
		view.set_read_only(True)
	
	def output_panel_show(self):
		sublime.active_window().run_command(
			"show_panel", {"panel": "output.clanglinter_panel"})
	
	def output_panel_hide(self):
		sublime.active_window().run_command(
			"hide_panel", {"panel": "output.clanglinter_panel"})
	
	def output_panel_clear(self, edit):
		view = sublime.active_window().create_output_panel("clanglinter_panel")
		
		#self.view.set_read_only(False)
		view.erase(edit, sublime.Region(0, view.size()))
		#self.view.set_read_only(True)
	
	def regions_create(self):
		view = sublime.active_window().active_view()
		
		region_error = []
		region_warning = []
		region_note = []
		
		scope_error = 'entity.name.tag'
		scope_warning = 'entity.other.attribute-name'
		scope_note = 'constant.other.symbol'
		#print(sublime.active_window().active_view().file_name())
		for line in range(len(parser.get_parameters())):
			if parser.get_parameters()[line]['file'] == view.file_name():
				if parser.get_parameters()[line]['flag'] == 'error' or 'fatal error':
					
					temp_line = parser.get_parameters()[line]['line'] - 1
					temp_column = parser.get_parameters()[line]['column'] - 1
					point_error = view.text_point(temp_line, temp_column)
					region_error.append(view.line(point_error))
					
				if parser.get_parameters()[line]['flag'] == 'warning':
					
					temp_line = parser.get_parameters()[line]['line'] - 1
					temp_column = parser.get_parameters()[line]['column'] - 1
					point_warning = view.text_point(temp_line, temp_column)
					region_warning.append(view.line(point_warning))
					
				if parser.get_parameters()[line]['flag'] == 'note':
					
					temp_line = parser.get_parameters()[line]['line'] - 1
					temp_column = parser.get_parameters()[line]['column'] - 1
					point_note = view.text_point(temp_line, temp_column)
					region_note.append(view.line(point_note))
					
		view.add_regions(
			'clanglinter_note', region_note, scope_note, 'dot',
			sublime.DRAW_OUTLINED)
		
		view.add_regions(
			'clanglinter_warning', region_warning, scope_warning, 'dot',
			sublime.DRAW_OUTLINED)
		
		view.add_regions(
			'clanglinter_error', region_error, scope_error, 'dot',
			sublime.DRAW_OUTLINED)
	
	def regions_output_panel(self, view, line):
		region_output_panel = []
		
		view.set_read_only(False)
		
		point_output_panel = view.text_point(line, 0)
		region_output_panel.append(
			view.line(point_output_panel))
		
		view.add_regions(
			'clanglinter_output_panel', region_output_panel, 'text', '',
			sublime.DRAW_OUTLINED)
		
		view.set_read_only(True)
	
	def regions_clear(self):
		view = sublime.active_window().active_view()
		view.erase_regions('clanglinter_note')
		view.erase_regions('clanglinter_warning')
		view.erase_regions('clanglinter_error')
		
ui = UserInterface()
settings = ClanglinterSettings()
context = ClanglinterContext()
utils = ClanglinterUtils()
parser = ClanglinterParser()


class SublimeEventListener(sublime_plugin.EventListener):
	def __init__(self):
		self.old_view = None
		self.wait_for_loading = False
	
	def on_post_save_async(self, view):
		window = sublime.active_window()
		
		if window.id() == context.get('window'):
			if (utils.check_extension(os.path.splitext(view.file_name())[1][1:]) and 
				utils.check_syntax(view)):
				
				start_thread(view)
	
	def on_selection_modified_async(self, view):
		window = sublime.active_window()
		if view.name() == 'clanglinter_panel':
			selected_line, _ = view.rowcol(view.sel()[0].begin())
			if selected_line < len(parser.get_parameters()):
				
				ui.regions_output_panel(view, selected_line)
				
				file = parser.get_parameters()[selected_line]['file']
				line = parser.get_parameters()[selected_line]['line']
				column = parser.get_parameters()[selected_line]['column']
				
				window.focus_group(context.get('group'))
				
				#column = parser.get_true_column(view, line, column)
				
				flags = "%s:%d:%d" % (file, line, column)
				window.open_file(flags, sublime.ENCODED_POSITION)
	
	def on_activated_async(self, view):
		if(view.name() != 'clanglinter_panel' and 
			view != self.old_view and 
			view.file_name()):
			
			self.old_view = view
			
			if(utils.check_extension(os.path.splitext(view.file_name())[1][1:])
				and utils.check_syntax(view)):
				
				if view.is_loading():
					self.wait_for_loading = True
				else:
					start_thread(view)
			else:
				ui.output_panel_hide()
	
	def on_load_async(self, view):
		if self.wait_for_loading:
			self.wait_for_loading = False
			start_thread(view)
	
	def on_close(self, view):
		if context.get('view') not in sublime.active_window().views():
			ui.output_panel_hide()
