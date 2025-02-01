import xmltodict

def xml_duplicate_remover(input_file_path: str, output_file_path: str):
    with open(input_file_path, 'r') as file:
        xml_data = file.read()

    data_dict = xmltodict.parse(xml_data)

    item_groups = data_dict['Project']['ItemGroup']
    unique_items = {}

    for item_group in item_groups:
        if 'Compile' in item_group:
            for compile_item in item_group['Compile']:
                if '@Include' in compile_item:
                    include_value = compile_item['@Include']
                    if include_value not in unique_items:
                        unique_items[include_value] = compile_item

    new_item_group = {'Compile': list(unique_items.values())}
    data_dict['Project']['ItemGroup'] = [new_item_group]

    new_xml_data = xmltodict.unparse(data_dict, pretty=True)

    with open(output_file_path, 'w') as file:
        file.write(new_xml_data)

    return f"Yinelenen öğeler kaldırıldı ve dosya '{output_file_path}' olarak kaydedildi."

settings = {
    "name": "XML Duplicate Remover",
    "enabled": True,
    "description": "Removes duplicate items from an XML file.",
}