library(shiny)
library(bslib)
library(dplyr)
library(ggplot2)

# Create fake data
set.seed(123)
n_responses <- 50
existing_data <- data.frame(
  role = sample(c("Business Analyst", "Data Analyst", "Data Scientist", "Data Engineer"), 
                n_responses, replace = TRUE),
  data_comfort = sample(1:5, n_responses, replace = TRUE),
  comm_comfort = sample(1:5, n_responses, replace = TRUE)
)

ui <- page_navbar(
  id = "navbar",
  header = NULL,  # Remove header
  fillable = TRUE,  # Make it fill the page
  
  nav_panel(
    title = "Survey",
    card(
      full_screen = TRUE,
      textOutput("current_q", container = function(...) {tags$script(...)}),
      # Question 1
      conditionalPanel(
        'output.current_q == 1',
        h3("Question 1 of 3"),
        radioButtons("role", "Which role best describes you?",
                    choices = c("Business Analyst", "Data Analyst", 
                              "Data Scientist", "Data Engineer")),
        actionButton("next1", "Next"),
        br(),
        actionLink("skip1", "Skip to results")
      ),
      
      # Question 2
      conditionalPanel(
        'output.current_q == 2',
        h3("Question 2 of 3"),
        sliderInput("data_comfort", 
                   "How comfortable are you manipulating data?",
                   min = 1, max = 5, value = 3, step = 1),
        actionButton("next2", "Next"),
        actionButton("prev2", "Previous"),
        br(),
        actionLink("skip2", "Skip to results")
      ),
      
      # Question 3
      conditionalPanel(
        'output.current_q == 3',
        h3("Question 3 of 3"),
        sliderInput("comm_comfort", 
                   "How comfortable are you communicating data?",
                   min = 1, max = 5, value = 3, step = 1),
        actionButton("submit", "Submit"),
        actionButton("prev3", "Previous"),
        br(),
        actionLink("skip3", "Skip to results")
      )
    )
  ),
  
  nav_panel(
    title = "Results",
    card(
      full_screen = TRUE,
      layout_columns(
        col_widths = c(3, 9),
        card(
          selectInput("role_filter", "Filter by Role:",
                     choices = c("All", 
                               unique(existing_data$role))),
        ),
        layout_columns(
          col_widths = c(6, 6),
          card(
            plotOutput("data_comfort_plot")
          ),
          card(
            plotOutput("comm_comfort_plot")
          )
        )
      )
    )
  )
)

server <- function(input, output, session) {
  # Initialize reactive values
  rv <- reactiveVal(1)  # Track current question
  responses <- reactiveVal(existing_data)
  
  # Navigation logic
  observeEvent(input$next1, {
    rv(2)
  })
  
  observeEvent(input$next2, {
    rv(3)
  })
  
  observeEvent(input$prev2, {
    rv(1)
  })
  
  observeEvent(input$prev3, {
    rv(2)
  })
  
  # Skip to results logic
  observeEvent(input$skip1, {
    updateNavbarPage(session, "navbar", selected = "Results")
  })
  
  observeEvent(input$skip2, {
    updateNavbarPage(session, "navbar", selected = "Results")
  })
  
  observeEvent(input$skip3, {
    updateNavbarPage(session, "navbar", selected = "Results")
  })
  
  # Submit response
  observeEvent(input$submit, {
    new_response <- data.frame(
      role = input$role,
      data_comfort = input$data_comfort,
      comm_comfort = input$comm_comfort
    )
    responses(rbind(responses(), new_response))
    updateNavbarPage(session, "navbar", selected = "Results")
  })
  
  # Plots
  output$data_comfort_plot <- renderPlot({
    data <- responses()
    if (input$role_filter != "All") {
      data <- data %>% filter(role == input$role_filter)
    }
    
    ggplot(data, aes(x = factor(data_comfort))) +
      geom_bar(fill = "steelblue") +
      labs(title = "Data Manipulation Comfort Level",
           x = "Comfort Level (1-5)",
           y = "Count") +
      theme_minimal()
  })
  
  output$comm_comfort_plot <- renderPlot({
    data <- responses()
    if (input$role_filter != "All") {
      data <- data %>% filter(role == input$role_filter)
    }
    
    ggplot(data, aes(x = factor(comm_comfort))) +
      geom_bar(fill = "forestgreen") +
      labs(title = "Data Communication Comfort Level",
           x = "Comfort Level (1-5)",
           y = "Count") +
      theme_minimal()
  })
  
  # Update current question
  output$current_q <- renderText({
    rv()
  })
  outputOptions(output, 'current_q', suspendWhenHidden = FALSE)
  
}

shinyApp(ui, server)