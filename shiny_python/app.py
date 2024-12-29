from shiny import App, reactive, render, ui, req
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Create fake data
np.random.seed(123)
n_responses = 50
roles = ["Business Analyst", "Data Analyst", "Data Scientist", "Data Engineer"]
existing_data = pd.DataFrame({
    "role": np.random.choice(roles, n_responses),
    "data_comfort": np.random.randint(1, 6, n_responses),
    "comm_comfort": np.random.randint(1, 6, n_responses)
})

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Survey",
        ui.card(
            ui.tags.script("""
            $(document).on("shiny:connected", function() {
                Shiny.addCustomMessageHandler("updateQuestion", function(message) {
                    Shiny.setInputValue("current_q", message);
                });
            });
            """),
            # Question 1
            ui.panel_conditional(
                "input.current_q === 1",
                ui.h3("Question 1 of 3"),
                ui.input_radio_buttons(
                    "role", "Which role best describes you?",
                    choices=roles
                ),
                ui.input_action_button("next1", "Next"),
                ui.br(),
                ui.input_action_button("skip1", "Skip to results", class_="action-button"),
            ),
            # Question 2
            ui.panel_conditional(
                "input.current_q === 2",
                ui.h3("Question 2 of 3"),
                ui.input_slider(
                    "data_comfort",
                    "How comfortable are you manipulating data?",
                    min=1, max=5, value=3, step=1
                ),
                ui.input_action_button("next2", "Next"),
                ui.input_action_button("prev2", "Previous"),
                ui.br(),
                ui.input_action_button("skip2", "Skip to results", class_="action-button"),
            ),
            # Question 3
            ui.panel_conditional(
                "input.current_q === 3",
                ui.h3("Question 3 of 3"),
                ui.input_slider(
                    "comm_comfort",
                    "How comfortable are you communicating data?",
                    min=1, max=5, value=3, step=1
                ),
                ui.input_action_button("submit", "Submit"),
                ui.input_action_button("prev3", "Previous"),
                ui.br(),
                ui.input_action_button("skip3", "Skip to results", class_="action-button"),
            ),
            full_screen=True
        )
    ),
    
    ui.nav_panel(
        "Results",
        ui.card(
            ui.layout_columns(
                ui.card(
                    ui.input_select(
                        "role_filter", "Filter by Role:",
                        choices=["All"] + list(existing_data["role"].unique())
                    )
                ),
                ui.layout_columns(
                    ui.card(ui.output_plot("data_comfort_plot")),
                    ui.card(ui.output_plot("comm_comfort_plot")),
                    col_widths=[6, 6]
                ),
                col_widths=[3, 9]
            ),
            full_screen=True
        )
    ),
    id="navbar",
    header=None,
    fillable=True
)

def server(input, output, session):
    # Initialize reactive values
    current_question = reactive.value(1)
    responses = reactive.value(existing_data)
    
    # Update current question in JavaScript
    @reactive.Effect
    async def _():
        await session.send_custom_message("updateQuestion", current_question.get())
    
    # Navigation logic
    @reactive.effect
    @reactive.event(input.next1)
    def _():
        current_question.set(2)
    
    @reactive.effect
    @reactive.event(input.next2)
    def _():
        current_question.set(3)
    
    @reactive.effect
    @reactive.event(input.prev2)
    def _():
        current_question.set(1)
    
    @reactive.effect
    @reactive.event(input.prev3)
    def _():
        current_question.set(2)
    
    # Skip to results logic
    @reactive.effect
    @reactive.event(input.skip1, input.skip2, input.skip3)
    def _():
        ui.update_navs("navbar", selected="Results")
    
    # Submit response
    @reactive.effect
    @reactive.event(input.submit)
    def _():
        new_response = pd.DataFrame({
            "role": [input.role()],
            "data_comfort": [input.data_comfort()],
            "comm_comfort": [input.comm_comfort()]
        })
        responses.set(pd.concat([responses.get(), new_response], ignore_index=True))
        ui.update_navs("navbar", selected="Results")
    
    @output
    @render.plot
    def data_comfort_plot():
        plt.figure(figsize=(8, 6))
        data = responses.get()
        if input.role_filter() != "All":
            data = data[data["role"] == input.role_filter()]
        
        plt.hist(data["data_comfort"], bins=np.arange(1, 7) - 0.5, 
                rwidth=0.8, color="steelblue")
        plt.title("Data Manipulation Comfort Level")
        plt.xlabel("Comfort Level (1-5)")
        plt.ylabel("Count")
        plt.grid(True, alpha=0.3)
    
    @output
    @render.plot
    def comm_comfort_plot():
        plt.figure(figsize=(8, 6))
        data = responses.get()
        if input.role_filter() != "All":
            data = data[data["role"] == input.role_filter()]
        
        plt.hist(data["comm_comfort"], bins=np.arange(1, 7) - 0.5, 
                rwidth=0.8, color="forestgreen")
        plt.title("Data Communication Comfort Level")
        plt.xlabel("Comfort Level (1-5)")
        plt.ylabel("Count")
        plt.grid(True, alpha=0.3)

app = App(app_ui, server)