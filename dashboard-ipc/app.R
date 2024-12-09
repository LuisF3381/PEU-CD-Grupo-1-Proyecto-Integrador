library(shiny)
library(ggplot2)
library(dplyr)
library(DT)
library(readr)

datos <- read.csv("datos_preprocesados.csv")
bases <- read.csv("Precio_Base_Online.csv")

datos <- na.omit(datos)

calculo_IPC <- function(mi_categoria){
  df <- datos %>%
    filter(categoria == mi_categoria) %>% 
    group_by(fechas) %>% 
    summarize(precio_prom = prod(price_numeric_escalado)^(1/n()),na.rm=TRUE)
  
  prod_geom <- prod(df$precio_prom)^(1/nrow(df))
  print(paste0("categoria: ",mi_categoria))
  
  ipc <- prod_geom * 100 / bases[bases$CLASIFICACION == paste0(" ", mi_categoria), "Precio_Base"]
  print(paste0("ipc: ",ipc))
  ipc_pond <- ipc*bases[bases$CLASIFICACION == paste0(" ", mi_categoria), "Peso_recalculado"]
  return(ipc_pond)
}

suma <- 0.0


for(categ in unique(datos$categoria)){
  if(categ != "HELADO DE HIELO PERSONAL"){
    ipc_pond <- calculo_IPC(categ)
    suma <- ipc_pond + suma 
  }
}

suma

ui <- fluidPage(
  titlePanel("Grupo 1 - Proyecto Integrador"),
  
  tags$head(
    tags$style(HTML("
      .igual_altura {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 250px;
        text-align: center;
      }
      
      .texto_editado {
        display: flex;
        justify-content: center;
        align-items: down;
        height: 80px;
        font-size: 40px; 
        font-weight: bold; 
        text-align: center;
      }
      
    "))
  ),
  
  # Filtros 
  fluidRow(
    column(6,
           wellPanel(
             class = "igual_altura",
             selectInput("f_categoria", "Selecciona Categoría:", 
                         choices = c("Todos", unique(datos$categoria))),
             selectInput("f_website", "Selecciona Sitio Web:", 
                         choices = c("Todos", unique(datos$website))),
             dateRangeInput("f_fechas", "Rango de Fechas:", 
                            start = min(datos$fechas, na.rm = TRUE), 
                            end = max(datos$fechas, na.rm = TRUE))
           )
    ),
    # Valores IPC 
    column(3,
           wellPanel(
             class = "igual_altura",
             h4("IPC Alimentos y Bebidas NO alcohólicas"),
             div(class = "texto_editado",textOutput("ipc1"))  
           )
    ),
    column(3,
           wellPanel(
             class = "igual_altura",
             h4("IPC por Categoría con Respecto al Periodo Base"),
             div(class = "texto_editado",textOutput("ipc2")) 
           )
    )
    
  ),
  
  # KPIs 
  fluidRow(
    column(4, 
           wellPanel(
             h4("Precio Mínimo"),
             textOutput("min_precio")
           )
    ),
    column(4, 
           wellPanel(
             h4("Precio Máximo"),
             textOutput("max_precio")
           )
    ),
    column(4, 
           wellPanel(
             h4("Precio Promedio"),
             textOutput("avg_precio")
           )
    )
  ),
  
  # Gráficos de línea y boxplot 
  fluidRow(
    column(6,
           h3("Evolución de Precios"),
           plotOutput("plot_lineas")
    ),
    column(6,
           h3("Distribución de Precios"),
           plotOutput("plot_box")
    )
  ),
  
  # Gráfico de barras 
  fluidRow(
    column(12,
           h3("Precios Promedio por Sitio"),
           plotOutput("plot_barras")
    )
  ),
  
  # Tabla de detalle
  fluidRow(
    column(12,
           h3("Detalle de Precios"),
           DTOutput("tabla_detalle")
    )
  )
)

server <- function(input, output, session) {
  
  # Datos filtrados en base a los inputs
  datos_filtrados <- reactive({
    df <- datos
    
    # Filtrar por producto si no se selecciona "Todos"
    if (input$f_categoria != "Todos") {
      df <- df %>% filter(categoria == input$f_categoria)
    }
    
    # Filtrar por sitio si no se selecciona "Todos"
    if (input$f_website != "Todos") {
      df <- df %>% filter(website == input$f_website)
    }
    
    # Filtrar por rango de fechas seleccionado
    if (!is.null(input$f_fechas)) {
      df <- df %>% filter(fechas >= input$f_fechas[1] & fechas <= input$f_fechas[2])
    }
    
    return(df)
  })
  
  # KPIs
  output$min_precio <- renderText({
    df <- datos_filtrados()
    if (nrow(df) > 0) {
      paste0("S/", round(min(df$price, na.rm = TRUE), 2))
    } else {
      "N/A"
    }
  })
  
  output$max_precio <- renderText({
    df <- datos_filtrados()
    if (nrow(df) > 0) {
      paste0("S/", round(max(df$price, na.rm = TRUE), 2))
    } else {
      "N/A"
    }
  })
  
  output$avg_precio <- renderText({
    df <- datos_filtrados()
    if (nrow(df) > 0) {
      paste0("S/", round(mean(df$price, na.rm = TRUE), 2))
    } else {
      "N/A"
    }
  })
  
  output$ipc1 <- renderText({
    
    ipc_estatico <- suma 
    
  })
  
  output$ipc2 <- renderText({
    
    if(input$f_categoria == "Todos"){
      ""
    }else{
      df <- datos_filtrados() 
      df_ipc2 <- df %>% 
        group_by(fechas) %>% 
        summarize(precio_prom = prod(price_numeric_escalado)^(1/n())) 
      
      prod_geom <- prod(df_ipc2$precio_prom)^(1/nrow(df_ipc2)) 
      
      ipc_dinamico <- prod_geom * 100 / bases[bases$CLASIFICACION == paste0(" ", input$f_categoria), "Precio_Base"]
      
      print(paste0("precio base ",bases[bases$CLASIFICACION == paste0(" ",input$f_categoria), "Precio_Base"] ))
      print(paste0("prod_geom ",prod_geom))
      print(paste0("ipc dinamico ", ipc_dinamico))
      
      ipc_dinamico
      
    }
  })
  
  # Gráfico de líneas (Evolución temporal de precios)
  output$plot_lineas <- renderPlot({
    df <- datos_filtrados()
    if (nrow(df) == 0) return(NULL) # Si no hay datos, no genera gráfico
    
    ggplot(df, aes(x = fechas, y = mean_price, group = website, color = website)) +
      geom_line() + geom_point() +
      labs(x = "Fecha", y = "Precio", color = "Sitio Web") +
      theme_minimal()
  })
  
  # Boxplot para distribución de precios por sitio
  output$plot_box <- renderPlot({
    df <- datos_filtrados()
    if (nrow(df) == 0) return(NULL) # Si no hay datos, no genera gráfico
    
    ggplot(df, aes(x = website, y = price, fill = website)) +
      geom_boxplot() +
      labs(x = "Sitio Web", y = "Precio") +
      theme_minimal()
  })
  
  # Gráfico de barras (Precio promedio por sitio)
  output$plot_barras <- renderPlot({
    df <- datos_filtrados()
    if (nrow(df) == 0) return(NULL) # Si no hay datos, no genera gráfico
    
    df_avg <- df %>% 
      group_by(website) %>% 
      summarize(precio_prom = mean(price, na.rm = TRUE))
    
    ggplot(df_avg, aes(x = reorder(website, precio_prom), y = precio_prom, fill = website)) +
      geom_col(show.legend = FALSE) +
      coord_flip() +
      labs(x = "Sitio Web", y = "Precio Promedio") +
      theme_minimal()
  })
  
  # Tabla detallada
  output$tabla_detalle <- renderDT({
    df <- datos_filtrados() %>%
      select(categoria, description, unidad, price, website, fechas) %>%
    rename(
      Categoría = categoria,
      Descripción = description,
      Unidad = unidad, 
      Precio = price,
      Web = website,
      Fecha = fechas
    )
    datatable(df, options = list(pageLength = 10))
  })
}


shinyApp(ui, server)


