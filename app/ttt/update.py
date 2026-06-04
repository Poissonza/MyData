from app.ttt.dbaccess import DBAccess

if __name__ == "__main__":
    dba = DBAccess()
    dba.update_tables()
    dba.team_win_ratio()
    dba.plot_teams("output/Pie Chart TTT.jpg")
    dba.close_conn()
