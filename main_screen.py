import copy
from copy import deepcopy
import flet
from flet import (AppBar, Colors, ElevatedButton, Card,Page, Column, Row, Container, Text, FilePicker, Icons, IconButton, SnackBar,
                  DataTable, WindowDragArea, DataColumn, DataCell, DataRow, NavigationRail, NavigationRailDestination,Stack,VerticalDivider,colors,icons)

from flet.utils import slugify
import json
import matplotlib.pyplot as plt
from sympy.codegen.cnodes import sizeof
import os
from function import fixed_point_iteration, plot_iterations


class ResponsiveMenuLayout(Row):
    def __init__(
        self,
        page,
        pages,
        *args,
        support_routes=True,
        menu_extended=True,
        minimize_to_icons=False,
        landscape_minimize_to_icons=False,
        portrait_minimize_to_icons=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.page = page
        self.pages = pages

        self._minimize_to_icons = minimize_to_icons
        self._landscape_minimize_to_icons = landscape_minimize_to_icons
        self._portrait_minimize_to_icons = portrait_minimize_to_icons
        self._support_routes = support_routes

        self.expand = True

        self.navigation_items = [navigation_item for navigation_item, _ in pages]
        self.routes = [
            f"/{item.pop('route', None) or slugify(item['label'])}"
            for item in self.navigation_items
        ]
        self.navigation_rail = self.build_navigation_rail()
        self.update_destinations()
        self._menu_extended = menu_extended
        self.navigation_rail.extended = menu_extended

        page_contents = [page_content for _, page_content in pages]

        self.menu_panel = Row(
            controls=[self.navigation_rail, VerticalDivider(width=1)],
            spacing=0,
            tight=True,
        )
        self.content_area = Column(page_contents, expand=True)

        self._was_portrait = self.is_portrait()
        self._panel_visible = self.is_landscape()

        self.set_navigation_content()

        if support_routes:
            self._route_change(page.route)
            self.page.on_route_change = self._on_route_change
        self._change_displayed_page()

        self.page.on_resized = self.handle_resize

    def select_page(self, page_number):
        self.navigation_rail.selected_index = page_number
        self._change_displayed_page()

    @property
    def minimize_to_icons(self) -> bool:
        return self._minimize_to_icons or (
            self._landscape_minimize_to_icons and self._portrait_minimize_to_icons
        )

    @minimize_to_icons.setter
    def minimize_to_icons(self, value: bool):
        self._minimize_to_icons = value
        self.set_navigation_content()

    @property
    def landscape_minimize_to_icons(self) -> bool:
        return self._landscape_minimize_to_icons or self._minimize_to_icons

    @landscape_minimize_to_icons.setter
    def landscape_minimize_to_icons(self, value: bool):
        self._landscape_minimize_to_icons = value
        self.set_navigation_content()

    @property
    def portrait_minimize_to_icons(self) -> bool:
        return self._portrait_minimize_to_icons or self._minimize_to_icons

    @portrait_minimize_to_icons.setter
    def portrait_minimize_to_icons(self, value: bool):
        self._portrait_minimize_to_icons = value
        self.set_navigation_content()

    @property
    def menu_extended(self) -> bool:
        return self._menu_extended

    @menu_extended.setter
    def menu_extended(self, value: bool):
        self._menu_extended = value

        dimension_minimized = (
            self.landscape_minimize_to_icons
            if self.is_landscape()
            else self.portrait_minimize_to_icons
        )
        if not dimension_minimized or self._panel_visible:
            self.navigation_rail.extended = value

    def _navigation_change(self, e):
        self._change_displayed_page()
        self.check_toggle_on_select()
        self.page.update()

    def _change_displayed_page(self):
        page_number = self.navigation_rail.selected_index
        if self._support_routes:
            self.page.route = self.routes[page_number]
        for i, content_page in enumerate(self.content_area.controls):
            content_page.visible = page_number == i

    def _route_change(self, route):
        try:
            page_number = self.routes.index(route)
        except ValueError:
            page_number = 0

        self.select_page(page_number)

    def _on_route_change(self, event):
        self._route_change(event.route)
        self.page.update()

    def build_navigation_rail(self):
        return NavigationRail(
            selected_index=0,
            label_type="none",
            on_change=self._navigation_change,
        )

    def update_destinations(self, icons_only=False):
        navigation_items = self.navigation_items
        if icons_only:
            navigation_items = deepcopy(navigation_items)
            for item in navigation_items:
                item.pop("label")

        self.navigation_rail.destinations = [
            NavigationRailDestination(**nav_specs) for nav_specs in navigation_items
        ]
        self.navigation_rail.label_type = "none" if icons_only else "all"

    def handle_resize(self, e):
        if self._was_portrait != self.is_portrait():
            self._was_portrait = self.is_portrait()
            self._panel_visible = self.is_landscape()
            self.set_navigation_content()
            self.page.update()

    def toggle_navigation(self, event=None):
        self._panel_visible = not self._panel_visible
        self.set_navigation_content()
        self.page.update()

    def check_toggle_on_select(self):
        if self.is_portrait() and self._panel_visible:
            self.toggle_navigation()

    def set_navigation_content(self):
        if self.is_landscape():
            self.add_landscape_content()
        else:
            self.add_portrait_content()

    def add_landscape_content(self):
        self.controls = [self.menu_panel, self.content_area]
        if self.landscape_minimize_to_icons:
            self.update_destinations(icons_only=not self._panel_visible)
            self.menu_panel.visible = True
            if not self._panel_visible:
                self.navigation_rail.extended = False
            else:
                self.navigation_rail.extended = self.menu_extended
        else:
            self.update_destinations()
            self.navigation_rail.extended = self._menu_extended
            self.menu_panel.visible = self._panel_visible

    def add_portrait_content(self):
        if self.portrait_minimize_to_icons and not self._panel_visible:
            self.controls = [self.menu_panel, self.content_area]
            self.update_destinations(icons_only=True)
            self.menu_panel.visible = True
            self.navigation_rail.extended = False
        else:
            if self._panel_visible:
                dismiss_shield = Container(
                    expand=True,
                    on_click=self.toggle_navigation,
                )
                self.controls = [
                    Stack(
                        controls=[self.content_area, dismiss_shield, self.menu_panel],
                        expand=True,
                    )
                ]
            else:
                self.controls = [
                    Stack(controls=[self.content_area, self.menu_panel], expand=True)
                ]
            self.update_destinations()
            self.navigation_rail.extended = self.menu_extended
            self.menu_panel.visible = self._panel_visible

    def is_portrait(self) -> bool:
        # Return true if window/display is narrow
        # return self.page.window_height >= self.page.window_width
        return self.page.height >= self.page.width

    def is_landscape(self) -> bool:
        # Return true if window/display is wide
        return self.page.width > self.page.height


if __name__ == "__main__":

    def main(page: Page, title="Fixed-Point Iteration Method"):
        page.title = title
        page.window.width = 960
        page.window.height = 540
        page.window.min_width = 960
        page.window.min_height = 540


        menu_button = IconButton(Icons.MENU)
        page.appbar = AppBar(
            leading=menu_button,
            leading_width=40,
            bgcolor=Colors.TEAL,
        )

        ########################################################################################################################################
        # JSON Input Section
        validated_data = None
        result = None

        json_file_picker = FilePicker(on_result=lambda e: handle_json_file(e, page))
        page.overlay.append(json_file_picker)

        def handle_json_file(e, page):
            if not e.files:
                json_feedback.value = "No file selected."
                page.update()
                return

            try:
                with open(e.files[0].path, "r") as f:
                    input_data = json.load(f)

                validate_json_input(input_data)
                nonlocal validated_data
                validated_data = copy.deepcopy(input_data)

                json_feedback.value = f"Loaded JSON file: {e.files[0].name}"
                page.overlay.append(SnackBar(Text("File loaded successfully!"), open=True))

            except Exception as ex:
                json_feedback.value = f"Error: {str(ex)}"
                page.overlay.append(SnackBar(Text("Failed to load file."), open=True))
            finally:
                page.update()

        def validate_json_input(data):
            required_keys = {"function", "initial_guess", "tolerance", "max_iterations"}
            if not all(key in data for key in required_keys):
                raise ValueError(f"Missing keys in JSON file. Required keys: {', '.join(required_keys)}")

        ########################################################################################################################################
        #Calculate Button
        def calculate_result(e, data):
            if data is None:
                page.overlay.append(SnackBar(Text("No JSON data to process."), open=True))
                return

            try:

                function = data["function"]
                initial_guess = data["initial_guess"]
                tolerance = data["tolerance"]
                max_iterations = data["max_iterations"]


                nonlocal result
                result = fixed_point_iteration(
                    func_str=function,
                    x_0=initial_guess,
                    tol=tolerance,
                    max_iter=max_iterations
                ),

                page.overlay.append(SnackBar(Text("Calculation completed and plot downloaded."), open=True))

            except Exception as ex:
                page.overlay.append(SnackBar(Text(f"An error occurred: {str(ex)}"), open=True))

        ########################################################################################################################################
        #SAVE

        # Placeholder for all iterations
        all_iterations = []

        def save_results_to_file(e):
            try:
                file_path = os.path.abspath("output_results.json")  # Use absolute path
                results = {"iterations": all_iterations}  # Save all iterations
                with open(file_path, "w") as json_file:
                    json.dump(results, json_file, indent=4)
                print(f"JSON results written to {file_path}")
                return file_path

            except Exception as e:
                print(f"Error saving results to file: {e}")
                return None

        if all_iterations is not None:
            for i in range(all_iterations.__len__()):
                iteration_result = {fixed_point_iteration(result["iterations"], result["x_value"])}
                all_iterations.append(iteration_result)


########################################################################################################################################
        # Buttons

        json_input_button = ElevatedButton(
            "Select JSON Input File",
            icon=Icons.UPLOAD_FILE,
            on_click=lambda e: json_file_picker.pick_files()
        )

        json_feedback = Text(value="", size=14, color="green")

        calculate_button = ElevatedButton(
            "Calculate",
            icon=Icons.CALCULATE_OUTLINED,
            on_click=lambda e: calculate_result(e,validated_data)
        )

        download_json_button = ElevatedButton(
            "Download JSON Results",
            icon=Icons.DOWNLOAD,
            on_click=lambda e: save_results_to_file(e)
        )

        ########################################################################################################################################

        pages = [
            (
                dict(
                    icon=Icons.HOME_SHARP,
                    selected_icon=Icons.HOME,
                    label="Homepage",
                ),
                create_page(
                    title="Homepage",
                    controls=
                    Column([
                        Row([
                            Container(content=json_input_button, padding=10),
                            Container(content=json_feedback, padding=10),],),

                        Container(content=calculate_button, padding=10),
                        Container(content=download_json_button, padding=10),
                    ],),
                ),
            ),
            # (
            #     dict(
            #         icon=Icons.AUTO_GRAPH_OUTLINED,
            #         selected_icon=Icons.AUTO_GRAPH,
            #         label="Animation",
            #     ),
            #
            #     create_page(
            #         title="Animation",
            #         body="Click Calculate to generate the fixed-point iteration plot.",
            #         controls=ElevatedButton(
            #             "View Animation",
            #             icon=Icons.PLAY_ARROW,
            #             on_click=lambda e: fixed_point_iteration(
            #                 func_str=validated_data["function"],
            #                 x_0=validated_data["initial_guess"],
            #                 tol=validated_data["tolerance"],
            #                 max_iter=validated_data["max_iterations"]
            #             )
            #         )
            #     ),
            # ),

            (
                dict(
                    icon=Icons.PEOPLE_OUTLINE,
                    selected_icon=Icons.PEOPLE,
                    label="Team",
                ),
                create_page(
                    title="Developer Team",
                    body=
                    "Çağrı KARTAL - 200315053" "\n"
                    "Abdullah Eren AYDOĞDU - 200315040" "\n"
                    "Eren ATASUN - 230315002" "\n"


                ),
            ),
            (
                dict(
                    icon=Icons.INFO_OUTLINE,
                    selected_icon=Icons.INFO,
                    label="Info",
                ),
                create_page(
                    "Info",
                    "Inputs:" "\n"
                    "- f(x): The function to find its root"  "\n"
                    "- x_0: The initial guess for iterative process" "\n"
                    "- tol: A value, which is very close to zero, to stop the iterations" "\n"
                    "- max_iter: The maximum number of iterations" "\n" "\n"
                    "Outputs:" "\n"
                    "- Iteration list as downloadable JSON file" "\n"
                    "- Plot Graph as downloadable PNG file" "\n"

                ),
            ),
        ]

        menu_layout = ResponsiveMenuLayout(page, pages)
        page.add(menu_layout)
        menu_button.on_click = lambda e: menu_layout.toggle_navigation()

    def create_page(title: str = None , body: str = None, controls: flet.Control = None):
        return Row(
            controls=[
                Column(
                    horizontal_alignment="stretch",
                    controls=[
                        Card(content=Container(Text(title, weight="bold"), padding=8)),
                        Text(body),
                        controls or Container()
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )

    def toggle_icons_only(menu: ResponsiveMenuLayout):
        menu.minimize_to_icons = not menu.minimize_to_icons
        menu.page.update()

    def toggle_menu_width(menu: ResponsiveMenuLayout):
        menu.menu_extended = not menu.menu_extended
        menu.page.update()

    flet.app(target=main)
