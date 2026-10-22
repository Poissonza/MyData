from DBAccess import DBAccess

DBA = DBAccess()
DBA.update_tables()
DBA.team_win_ratio()
DBA.plot_teams("Output/Pie Chart TTT.jpg")
DBA.close_conn()
