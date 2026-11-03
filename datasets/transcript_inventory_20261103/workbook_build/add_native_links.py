"""Attach native Excel hyperlinks to the artifact-tool authored workbook.

The artifact runtime does not implement HYPERLINK evaluation or a link-range
API. Keep displayed labels authored by artifact-tool, then add standard OOXML
link relationships so links work without requiring a recalculation.
"""
import json
import posixpath
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as ET

MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
workbook_path = Path(sys.argv[1])
links = json.loads(Path(sys.argv[2]).read_text())
with ZipFile(workbook_path) as z:
    entries = {n: z.read(n) for n in z.namelist()}
workbook = ET.fromstring(entries['xl/workbook.xml'])
relations = ET.fromstring(entries['xl/_rels/workbook.xml.rels'])
targets = {r.get('Id'): r.get('Target') for r in relations}
sheet_paths = {}
for sheet in workbook.findall(f'{{{MAIN}}}sheets/{{{MAIN}}}sheet'):
    target = targets[sheet.get(f'{{{REL}}}id')]
    sheet_paths[sheet.get('name')] = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)

late_elements = {
    'printOptions', 'pageMargins', 'pageSetup', 'headerFooter', 'rowBreaks',
    'colBreaks', 'customProperties', 'cellWatches', 'ignoredErrors', 'smartTags',
    'drawing', 'legacyDrawing', 'legacyDrawingHF', 'picture', 'oleObjects',
    'controls', 'webPublishItems', 'tableParts', 'extLst',
}
external_count = internal_count = 0
for name, xml_path in sheet_paths.items():
    sheet_links = [x for x in links if x['sheet'] == name]
    if not sheet_links:
        continue
    root = ET.fromstring(entries[xml_path])
    hyperlink_parent = root.find(f'{{{MAIN}}}hyperlinks')
    if hyperlink_parent is None:
        hyperlink_parent = ET.Element(f'{{{MAIN}}}hyperlinks')
        before = next((i for i, child in enumerate(root) if ET.QName(child).localname in late_elements), len(root))
        root.insert(before, hyperlink_parent)
    rel_path = posixpath.join(posixpath.dirname(xml_path), '_rels', posixpath.basename(xml_path) + '.rels')
    rels = ET.fromstring(entries[rel_path]) if rel_path in entries else ET.Element(f'{{{PKG}}}Relationships', nsmap={None: PKG})
    used = {r.get('Id') for r in rels}
    for i, link in enumerate(sheet_links, 1):
        item = ET.SubElement(hyperlink_parent, f'{{{MAIN}}}hyperlink', ref=link['cell'])
        if link['url'].startswith('#'):
            item.set('location', link['url'][1:])
            internal_count += 1
        else:
            rid = f'rIdNativeLink{i}'
            assert rid not in used
            used.add(rid)
            item.set(f'{{{REL}}}id', rid)
            ET.SubElement(rels, f'{{{PKG}}}Relationship', Id=rid, Type=REL + '/hyperlink', Target=link['url'], TargetMode='External')
            external_count += 1
    entries[xml_path] = ET.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    entries[rel_path] = ET.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)

temp = workbook_path.with_suffix('.native-links.xlsx')
with ZipFile(temp, 'w', ZIP_DEFLATED) as z:
    for name, content in entries.items():
        z.writestr(name, content)
temp.replace(workbook_path)
print(json.dumps({'native_external_links': external_count, 'native_internal_links': internal_count}))
