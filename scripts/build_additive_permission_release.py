import argparse,json
from datetime import date
from pathlib import Path
import yaml
from food_kg.services.additive_permission_release import build,write,SOURCE_ID

p=argparse.ArgumentParser();p.add_argument('--staging',type=Path,action='append',required=True);p.add_argument('--additives',type=Path,required=True);p.add_argument('--scope',type=Path);p.add_argument('--nodes-output',type=Path,required=True);p.add_argument('--relationships-output',type=Path,required=True);p.add_argument('--release-output',type=Path,required=True);p.add_argument('--version',required=True);p.add_argument('--reviewed-at',default=date.today().isoformat());a=p.parse_args()
rows=[json.loads(line) for path in a.staging for line in path.read_text(encoding='utf-8').splitlines()]
scope=yaml.safe_load(a.scope.read_text(encoding='utf-8')) if a.scope else None
nodes,rels=build(rows,json.loads(a.additives.read_text(encoding='utf-8')),a.reviewed_at,scope)
write(a.nodes_output,nodes);write(a.relationships_output,rels)
a.release_output.write_text(yaml.safe_dump({'version':a.version,'released_at':a.reviewed_at,'source_ids':[SOURCE_ID],'node_count':len(nodes),'relationship_count':len(rels),'notes':'Appendix 2A additive maximum-use limits.'},allow_unicode=True,sort_keys=False),encoding='utf-8')
print(f'Built {a.version}: {len(nodes)} nodes, {len(rels)} relationships')
