import pymysql
import configparser
import csv


def readConfig(configFile):
    config = configparser.ConfigParser()
    try:
        config.read_file(open(configFile))
        dbConfig = {
            "host": config['csc']['dbhost'],
            "user": config['csc']['dbuser'],
            "password": config['csc']['dbpw']
        }
        return dbConfig
    except FileNotFoundError as e:
        print(f"{configFile} was not found")
        raise


def connectToDatabase(dbName, configFile):
    dbConfig = readConfig(configFile)
    dbConn = pymysql.connect(host=dbConfig["host"],
                             user=dbConfig["user"],
                             passwd=dbConfig["password"],
                             db=dbName,
                             use_unicode=True,
                             charset='utf8mb4',
                             autocommit=True)
    return dbConn


def disconnectFromDatabase(dbConn):
    dbConn.close()


def processFile(fileName, dbConn):
    batchSize = 100
    with open(fileName) as statFile:
        statFileReader = csv.DictReader(statFile)
        batchCounter = 1

        # Dictionary to track unique player-game combinations with seasonID, gameID, and playerID
        playerGameMap = {}
        # List to track positions for each player-game
        positionList = []

        for statDictionary in statFileReader:
            row_data = processRow(dbConn, statDictionary)
            if row_data is not None:
                key = (row_data['seasonID'], row_data['gameID'], row_data['playerID'])

                # Only keep the first occurrence of each player-game combo
                if key not in playerGameMap:
                    playerGameMap[key] = row_data['stats']

                # Track all positions for this player-game
                for posID in row_data['positionIDs']:
                    positionList.append((
                        row_data['seasonID'],
                        row_data['gameID'],
                        row_data['playerID'],
                        posID
                    ))

            if (batchCounter == batchSize):
                if playerGameMap:
                    saveStatBatch(dbConn, list(playerGameMap.values()))
                if positionList:
                    savePositionBatch(dbConn, positionList)
                playerGameMap = {}
                positionList = []
                batchCounter = 1
            else:
                batchCounter += 1

        # Save remaining rows
        if playerGameMap:
            saveStatBatch(dbConn, list(playerGameMap.values()))
        if positionList:
            savePositionBatch(dbConn, positionList)


def processRow(dbConn, statDictionary):
    statDictionary = cleanDictionary(statDictionary)

    print(
        f"\nProcessing row: Season={statDictionary.get('Season')}, Date={statDictionary.get('Date')}, Player={statDictionary.get('firstName')} {statDictionary.get('lastName')}")

    try:
        seasonID = getSeasonID(dbConn, statDictionary["Season"])
        opponentID = getOpponentID(dbConn, statDictionary["Opp"])
        playerID = getPlayerID(dbConn, statDictionary["firstName"], statDictionary["lastName"])
        gameID = getGameID(dbConn, statDictionary["Date"], statDictionary["teamResult"], opponentID, seasonID)

        # Get position IDs for Position1, Position2, Position3
        positionIDs = []
        for pos_col in ["Postion1", "Position2", "Position3"]:
            if statDictionary.get(pos_col):
                posID = getPositionID(dbConn, statDictionary[pos_col])
                if posID is not None:
                    positionIDs.append(posID)

    except KeyError as e:
        print(f"ERROR: Column {e} not found in CSV. Available columns are: {list(statDictionary.keys())}")
        return None

    print(
        f"IDs - seasonID={seasonID}, opponentID={opponentID}, playerID={playerID}, gameID={gameID}, positionIDs={positionIDs}")

    if seasonID is None or gameID is None or playerID is None:
        print(f"WARNING: Skipping row due to missing required data")
        return None

    return {
        'seasonID': seasonID,
        'gameID': gameID,
        'playerID': playerID,
        'positionIDs': positionIDs,
        'stats': (
            seasonID, gameID, playerID, statDictionary["PA"], statDictionary["AB"], statDictionary["H"],
            statDictionary["HR"], statDictionary["BB"], statDictionary["SO"], statDictionary["TB"],
            statDictionary["WPA"], statDictionary["SB"]
        )
    }


def cleanDictionary(initialDictionary):
    cleanDictionary = {}
    for key, value in initialDictionary.items():
        if value == "":
            cleanDictionary[key] = None
        else:
            cleanDictionary[key] = value
    return cleanDictionary


def saveStatBatch(dbConn, batchSQLStatementValues):
    statInsertSQL = 'INSERT INTO project_player_has_game ' \
                    '(seasonID, gameID, playerID, plateAppearances, atBats, hits, homeRuns, walks, strikeOuts, totalBases, ' \
                    'winProbabilityAdded, stolenBases) ' \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    cursor = dbConn.cursor()
    cursor.executemany(statInsertSQL, batchSQLStatementValues)
    cursor.close()


def savePositionBatch(dbConn, batchSQLStatementValues):
    positionInsertSQL = 'INSERT IGNORE INTO project_player_game_has_position ' \
                        '(seasonID, gameID, playerID, positionID) ' \
                        'VALUES (%s, %s, %s, %s);'
    cursor = dbConn.cursor()
    cursor.executemany(positionInsertSQL, batchSQLStatementValues)
    cursor.close()


def getSeasonID(dbConn, year):
    if year is None:
        return None

    # Convert year to int
    try:
        yearInt = int(year)
    except (ValueError, TypeError):
        return None

    selectSQL = "SELECT seasonID FROM project_season WHERE year = %s"
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(selectSQL, [yearInt])
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        return result['seasonID']

    # Insert new season
    insertSQL = "INSERT INTO project_season (year) VALUES (%s)"
    cursor = dbConn.cursor()
    cursor.execute(insertSQL, [yearInt])
    cursor.execute("SELECT LAST_INSERT_ID()")
    auto_incremented_key = cursor.fetchone()[0]
    cursor.close()
    return auto_incremented_key


def getOpponentID(dbConn, teamName):
    if teamName is None:
        return None

    selectSQL = "SELECT opponentID FROM project_opponent WHERE teamName = %s"
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(selectSQL, [teamName])
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        return result['opponentID']

    insertSQL = "INSERT INTO project_opponent (teamName) VALUES (%s)"
    cursor = dbConn.cursor()
    cursor.execute(insertSQL, [teamName])
    cursor.execute("SELECT LAST_INSERT_ID()")
    auto_incremented_key = cursor.fetchone()[0]
    cursor.close()
    return auto_incremented_key


def getGameID(dbConn, date, result, opponentID, seasonID):
    if date is None or seasonID is None or opponentID is None:
        return None

    selectSQL = "SELECT gameID FROM project_game WHERE date = %s AND seasonID = %s"
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(selectSQL, [date, seasonID])
    resultRow = cursor.fetchone()
    cursor.close()

    if resultRow is not None:
        return resultRow['gameID']

    insertSQL = "INSERT INTO project_game (seasonID, opponentID, result, date) VALUES (%s, %s, %s, %s)"
    cursor = dbConn.cursor()
    cursor.execute(insertSQL, (seasonID, opponentID, result, date))
    cursor.execute("SELECT LAST_INSERT_ID()")
    auto_incremented_key = cursor.fetchone()[0]
    cursor.close()
    return auto_incremented_key


def getPlayerID(dbConn, firstName, lastName):
    if firstName is None or lastName is None:
        return None

    selectSQL = "SELECT playerID FROM project_player WHERE firstName = %s AND lastName = %s"
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(selectSQL, [firstName, lastName])
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        return result['playerID']

    insertSQL = "INSERT INTO project_player (firstName, lastName) VALUES (%s, %s)"
    cursor = dbConn.cursor()
    cursor.execute(insertSQL, (firstName, lastName))
    cursor.execute("SELECT LAST_INSERT_ID()")
    auto_incremented_key = cursor.fetchone()[0]
    cursor.close()
    return auto_incremented_key


def getPositionID(dbConn, positionName):
    if positionName is None:
        return None

    selectSQL = "SELECT positionID FROM project_position WHERE positionName = %s"
    cursor = dbConn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(selectSQL, [positionName])
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        return result['positionID']

    # Insert new position - positionID will auto-increment
    insertSQL = "INSERT INTO project_position (positionName) VALUES (%s)"
    cursor = dbConn.cursor()
    cursor.execute(insertSQL, [positionName])
    cursor.execute("SELECT LAST_INSERT_ID()")
    auto_incremented_key = cursor.fetchone()[0]
    cursor.close()
    print(f"Inserted positionID = {auto_incremented_key}")
    return auto_incremented_key


# Start Main Program
if (__name__ == '__main__'):
    dbSchema = 'roconnor7'
    configFile = 'projCredentials.txt'
    dataFile = 'SoxOutfieldStats.csv'
    try:
        # 1. Connect To Database
        dbConn = connectToDatabase(dbSchema, configFile)

        try:
            # 2 Process the File
            processFile(dataFile, dbConn)

        except Exception as e:
            print(e)

        finally:
            # 3 Close DB Connection
            disconnectFromDatabase(dbConn)
    except Exception as e:
        print(e)
