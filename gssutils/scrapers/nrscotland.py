import mimetypes
from urllib.parse import urljoin

from gssutils.metadata import GOV
from gssutils.metadata.dcat import Distribution


def scrape(scraper, tree):
    scraper.dataset.publisher = GOV['national-records-of-scotland']
    scraper.dataset.title = tree.xpath('//div[@property = "dc:title"]/h2/text()')[0].strip()
    after_background = tree.xpath(
        '//h3[contains(descendant-or-self::*[text()], "Background")]/following-sibling::*')
    description_nodes = []
    for node in after_background:
        if node.tag != 'h3':
            description_nodes.append(node)
        else:
            break
    scraper.dataset.description = scraper.to_markdown(description_nodes)
    data_nodes = tree.xpath(
        '//h3[contains(descendant-or-self::*[text()], "Data")]/following-sibling::*/child::strong')
    for node in data_nodes:
        for anchor in node.xpath('following-sibling::a'):
            file_type = anchor.text.strip().lower()
            if file_type in ['excel', 'csv']:
                distribution = Distribution(scraper)
                distribution.downloadURL = urljoin(scraper.uri, anchor.get('href'))
                distribution.title = node.text.strip()
                distribution.mediaType = {
                    'csv': 'text/csv',
                    'excel': 'application/vnd.ms-excel'
                }.get(
                    file_type,
                    mimetypes.guess_type(distribution.downloadURL)[0]
                )
                scraper.distributions.append(distribution)
