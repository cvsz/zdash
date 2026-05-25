class TwinReportService:
    def __init__(self,snap): self.snap=snap; self._reports=[]
    def generate_twin_report(self,org,ws,name='latest'):
        snaps=self.snap.list_snapshots(org,ws); data={'id':f'report-{len(self._reports)+1}','name':name,'assumptions':['simulation model'],'limitations':['advisory only'],'snapshot_count':len(snaps)}
        self._reports.append((org,ws,data)); return data
    def build_markdown_report(self,report): return f"# Twin Report

Name: {report['name']}

## Assumptions
- "+'
- '.join(report['assumptions'])+"

## Limitations
- "+'
- '.join(report['limitations'])
    def list_reports(self,org,ws): return [r for o,w,r in self._reports if o==org and w==ws]
