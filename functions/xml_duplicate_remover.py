import xmltodict

def xml_duplicate_remover(input_file_path: str, output_file_path: str):
    """
    XML dosyasındaki yinelenen öğeleri kaldırır ve temizlenmiş XML'i yeni bir dosyaya kaydeder.

    :param input_file: Yinelenen öğelerin bulunduğu XML dosyasının yolu.
    :param output_file: Temizlenmiş XML'in kaydedileceği dosyanın yolu.
    """
    # XML dosyasını oku
    with open(input_file_path, 'r') as file:
        xml_data = file.read()

    # XML'i sözlüğe dönüştür
    data_dict = xmltodict.parse(xml_data)

    # Yinelenen öğeleri kaldır
    item_groups = data_dict['Project']['ItemGroup']
    unique_items = {}

    for item_group in item_groups:
        if 'Compile' in item_group:
            for compile_item in item_group['Compile']:
                if '@Include' in compile_item:
                    include_value = compile_item['@Include']
                    if include_value not in unique_items:
                        unique_items[include_value] = compile_item

    # Yeni ItemGroup oluştur
    new_item_group = {'Compile': list(unique_items.values())}
    data_dict['Project']['ItemGroup'] = [new_item_group]

    # Sözlüğü tekrar XML'e dönüştür
    new_xml_data = xmltodict.unparse(data_dict, pretty=True)

    # Temizlenmiş XML'i yeni dosyaya yaz
    with open(output_file_path, 'w') as file:
        file.write(new_xml_data)

    return f"Yinelenen öğeler kaldırıldı ve dosya '{output_file_path}' olarak kaydedildi."