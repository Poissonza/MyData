class XMLTools:

    def __init__(self, xml_data):
        self._xml_data = xml_data

    def fetch_element(self, element, attribute=None, convert=None):

        element_data = self._xml_data.find(element)
        if attribute:
            element_data = element_data.attrib[attribute]

        if convert:
            element_data = convert(element_data)
        return element_data

    def fetch_element_list(self, element, attribute=None, convert=None):
        list_res = []
        for item in self._xml_data.findall(element):
            if attribute:
                list_res.append(item.attrib[attribute])

        return list_res
