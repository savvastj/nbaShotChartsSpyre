from spyre import server

import matplotlib.pyplot as plt
import pandas as pd
import nbaShotCharts as nba

from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.resources import INLINE
from bokeh.resources import CDN
from bokeh.embed import components

class ShotChartApp(server.App):
    title = "NBA Shot Charts"

    # One dict per input
    inputs = [  {"type":"text", 
                    "key":"player",  # feeds to param dict
                    "label": "Enter Player: Last Name, First \n Name",
                    "value": "Harden, James"},
                    # "action_id":"update_data"},

                {"type": "dropdown",
                    "label": "Season",
                    "options": [
                        {"label": "2014-15", "value": "2014-15"},
                        {"label": "2013-14", "value": "2013-14"},
                        {"label": "2012-13", "value": "2012-13"},
                        {"label": "2011-12", "value": "2011-12"},
                        {"label": "2010-11", "value": "2010-11"},
                        {"label": "2009-10", "value": "2009-10"},
                        {"label": "2008-09", "value": "2008-09"},
                        {"label": "2007-08", "value": "2007-08"},
                        {"label": "2006-07", "value": "2006-07"},
                        {"label": "2005-06", "value": "2005-06"},
                        {"label": "2004-05", "value": "2004-05"},
                        {"label": "2003-04", "value": "2003-04"},
                        {"label": "2002-03", "value": "2002-03"},
                        {"label": "2001-02", "value": "2001-02"}],
                    "key": "season"},#,
                    # "action_id":"update_data"}]   # connect input to control
                {"type":'dropdown',
                    "label": 'Bottom Chart', 
                    "options" : [
                        {"label": "FG% Heatmap", "value":"heatmap"},
                        {"label": "FGA Hexbin Chart", "value":"hexbin"},
                        {"label": "FGA Scatter Chart", "value":"scatter"},
                        {"label": "FGA Density Chart", "value":"kde"}
                        ],
                    "key": 'plot',
                    "action_id":"update_static"}]

    outputs = [{"type" : "html",
                    "id" : "title_HTML",
                    "control_id" : "update_data"},
                {"type" : "html",
                    "id" : "bokeh_chart",
                    "control_id" : "update_data"},
                
                {"type": "plot",
                    "control_id": "update_data",
                    "id": "shot_chart"}
                ]

    controls = [{"type": "button",
                    "label": "Update Charts",
                    "id": "update_data"}]

    def  getData(self, params):
        player = params["player"]
        season = params["season"]
        player_id = nba.Players().get_player_id(player)
        player_shots = nba.Shots(player_id[0], season=season).get_shots()
        player_shots.insert(0, "Season", season)
        return player_shots

    def title_HTML(self, params):
        name = " ".join(params["player"].split(", ")[::-1])
        season = params["season"]
        player_id = nba.Players().get_player_id(params["player"])[0]
        if name != "Dwyane Wade":
            img = "http://stats.nba.com/media/players/230x185/{}.png".format(player_id)
            html = """
            <html>
                <div style="padding-left:10px; float:top">
                    <img src={img} style="float:top" height="115">
                    <font size="4" style="padding-left:70px">FGA {season} Reg. Season</font>
                </div>    
            </html>
            """.format(img=img, name=name, season=season)
        # Dwyane Wade's MC Hammer Outfit
        else:
            # img = "http://morethan-stats.com/wp-content/uploads/2015/08/Dwyane-Wade-esquire-mag-feature.png"
            img = "http://www.trbimg.com/img-55cd0fb3/turbine/sfl-miami-heat-dwyane-wade-081215"
            html = """
            <html>
                <div style="padding-left:220px; float:top">
                    <img src={img} style="float:top" height="150">
                </div>    
                    <font size="4" style="padding-left:220px">FGA {season} Reg. Season</font>

            </html>
            """.format(img=img, name=name, season=season)
        return html

    def shot_chart(self, params):
        player_shots = self.getData(params)
        name = " ".join(params["player"].split(", ")[::-1])
        if params["plot"] == "scatter":
            title = name+" FGA "+params["season"]+" Reg. Season"
            shot_chart = nba.shot_chart_jointgrid(player_shots.LOC_X,
                                                  player_shots.LOC_Y, 
                                                  alpha=0.5,
                                                  marginals_type='hist',
                                                  title=title,
                                                  size=(6*1.65,5.5*1.65))
            return shot_chart.fig

        elif params["plot"] == "hexbin":
            title = name+" FGA "+params["season"]+" Reg. Season"
            shot_chart = nba.shot_chart_jointgrid(player_shots.LOC_X,
                                                  player_shots.LOC_Y,
                                                  joint_type="hex",
                                                  marginals_type='hist',
                                                  # hex_gridsize=10,
                                                  cmap=plt.cm.gist_heat_r,
                                                  marginals_color=plt.cm.gist_heat_r(.2),
                                                  title=title,
                                                  size=(6*1.65,5.5*1.65))
            return shot_chart.fig

        elif params["plot"] == "kde":
            title = name+" FGA "+params["season"]+" Reg. Season"
            shot_chart = nba.shot_chart_jointgrid(player_shots.LOC_X,
                                                  player_shots.LOC_Y,
                                                  joint_type="kde",
                                                  marginals_type='kde',
                                                  marginals_color=plt.cm.gist_heat_r(.2),
                                                  cmap=plt.cm.gist_heat_r,
                                                  n_levels=50,
                                                  # alpha=0.9,
                                                  title=title,
                                                  size=(6*1.65,5.5*1.65))
            return shot_chart.fig

        elif params["plot"]=="heatmap":
            plt.figure(figsize=(7*1.65,5.5*1.65))
            title = name+" FG% "+params["season"]+" Reg. Season"
            im = nba.heatmap_fgp(player_shots.LOC_X, player_shots.LOC_Y,
                                     player_shots.SHOT_MADE_FLAG,
                                     title=title)
            plt.colorbar(im)
            fig = im.get_figure()
            return fig


    def bokeh_chart(self, params):
        player_shots = self.getData(params)
        source = ColumnDataSource(player_shots)

        plot = nba.bokeh_shot_chart(source)

        hover = HoverTool(renderers = [plot.renderers[0]],
                  tooltips=[("Shot Index", "$index"),
                            ("Shot Outcome", "@EVENT_TYPE"),
                            ("Shot Type", "@SHOT_TYPE"),
                            ("Action Type", "@ACTION_TYPE"),
                            ("Shot Distance", "@SHOT_DISTANCE ft")])

        plot.add_tools(hover)

        script, div = components(plot, CDN)
        html = "%s\n%s"%(script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]


app = ShotChartApp()
app.launch(port=5000)