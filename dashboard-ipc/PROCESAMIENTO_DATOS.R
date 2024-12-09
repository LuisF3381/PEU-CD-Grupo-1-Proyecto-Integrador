# procesamiento de los datos

library(stringr) 
library(dplyr)

df <- read.csv("C:/Users/c3318/OneDrive/2024/PEU CD/proyecto integrador/ejemplos/app_02/datos_concatenados.csv")


############### cleaning data ##############
#nulos
df <- df[!is.na(df$price_numeric), ]

#ordenar columna categorias
df <- df[order(df$categoria), ]

# data type
# fechas
df <- df %>%
  mutate(fechas = str_sub(scrape_timestamp, 1, 10))
df$fechas  <- as.Date(df$fechas) 

# Rename columns
df <- df %>%
  rename(
    price = price_numeric
  )

# redondeando cantidad
df$cantidad <- as.integer(df$cantidad)

head(df)# select columns
#df <- df %>%
#  select(categoria, description, price, unidad, price, website, fechas)

sapply(df, class)


# Renombrar los valores únicos de la columna 'website'
df <- df %>%
  mutate(website = recode(website,
                          "metro" = "Metro",
                          "plaza_vea" = "Plaza Vea",
                          "wong" = "Wong",
                          "vivanda" = "Vivanda",
                          "vega" = "Vega",
                          "tottus" = "Tottus"))

#### outliers ###
df <- df %>%
  group_by(categoria, fechas) %>%
  mutate(
    q1 = quantile(price, 0.25, na.rm = TRUE),
    q3 = quantile(price, 0.75, na.rm = TRUE),
    iqr = q3 - q1,
    limite_inferior = q1 - 1.5 * iqr,
    limite_superior = q3 + 1.5 * iqr
  ) %>%
  filter(price >= limite_inferior & price <= limite_superior) %>%
  select(-q1, -q3, -iqr, -limite_inferior, -limite_superior) %>% # Opcional: eliminar columnas auxiliares
  ungroup()

############## calculos ###############
df <- df %>%
  group_by(categoria, fechas, website) %>%
  mutate(mean_price = mean(price)) %>%
  ungroup() 

write.csv(df, "C:/Users/c3318/OneDrive/2024/PEU CD/proyecto integrador/ejemplos/app_03/datos_preprocesados.csv", row.names = FALSE





