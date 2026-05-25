from .models import PluginManifest
BUILTINS=[
PluginManifest(id='zdash-risk-summary',name='Risk Summary',slug='zdash-risk-summary',version='1.0.0',description='summarize latest risk state',author='zDash',category='risk'),
PluginManifest(id='zdash-backtest-reporter',name='Backtest Reporter',slug='zdash-backtest-reporter',version='1.0.0',description='generate markdown report',author='zDash',category='backtesting'),
PluginManifest(id='zdash-content-calendar',name='Content Calendar',slug='zdash-content-calendar',version='1.0.0',description='summarize scheduled content',author='zDash',category='content'),
PluginManifest(id='zdash-scheduler-health',name='Scheduler Health',slug='zdash-scheduler-health',version='1.0.0',description='summarize scheduler job health',author='zDash',category='automation'),]
