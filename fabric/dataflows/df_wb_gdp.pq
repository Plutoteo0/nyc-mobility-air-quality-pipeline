let
  Источник = Json.Document(Web.Contents("https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json&per_page=100")),
  #"Преобразовано в таблицу" = Table.FromList(Источник, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
  #"Детализация углублением" = #"Преобразовано в таблицу"{1}[Column1],
  #"Преобразовано в таблицу 1" = Table.FromList(#"Детализация углублением", Splitter.SplitByNothing(), null, null, ExtraValues.Error),
  #"Развернуто: Column1" = Table.ExpandRecordColumn(#"Преобразовано в таблицу 1", "Column1", {"date", "value"}, {"date", "value"}),
  #"Измененный тип столбца" = Table.TransformColumnTypes(#"Развернуто: Column1", {{"date", type number}, {"value", type number}}, "en-US"),
  #"Измененный тип столбца 1" = Table.TransformColumnTypes(#"Измененный тип столбца", {{"date", Int64.Type}})
in
  #"Измененный тип столбца 1"