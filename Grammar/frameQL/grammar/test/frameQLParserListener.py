# Generated from frameQLParser.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .frameQLParser import frameQLParser
else:
    from frameQLParser import frameQLParser

# This class defines a complete listener for a parse tree produced by frameQLParser.
class frameQLParserListener(ParseTreeListener):

    def __init__(self):
        self.temp_split_list = []    # temporary list storing a splitted predicate
        self.predicate_list = []    # temporary list storing the predicates
        self.output_predicate = []
        self.output_operator = []
        #self.bothInParentheses = False

    # Enter a parse tree produced by frameQLParser#root.
    def enterRoot(self, ctx:frameQLParser.RootContext):
        pass

    # Exit a parse tree produced by frameQLParser#root.
    def exitRoot(self, ctx:frameQLParser.RootContext):
        pass


    # Enter a parse tree produced by frameQLParser#sqlStatements.
    def enterSqlStatements(self, ctx:frameQLParser.SqlStatementsContext):
        pass

    # Exit a parse tree produced by frameQLParser#sqlStatements.
    def exitSqlStatements(self, ctx:frameQLParser.SqlStatementsContext):
        pass


    # Enter a parse tree produced by frameQLParser#sqlStatement.
    def enterSqlStatement(self, ctx:frameQLParser.SqlStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#sqlStatement.
    def exitSqlStatement(self, ctx:frameQLParser.SqlStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#emptyStatement.
    def enterEmptyStatement(self, ctx:frameQLParser.EmptyStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#emptyStatement.
    def exitEmptyStatement(self, ctx:frameQLParser.EmptyStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#ddlStatement.
    def enterDdlStatement(self, ctx:frameQLParser.DdlStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#ddlStatement.
    def exitDdlStatement(self, ctx:frameQLParser.DdlStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#dmlStatement.
    def enterDmlStatement(self, ctx:frameQLParser.DmlStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#dmlStatement.
    def exitDmlStatement(self, ctx:frameQLParser.DmlStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#transactionStatement.
    def enterTransactionStatement(self, ctx:frameQLParser.TransactionStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#transactionStatement.
    def exitTransactionStatement(self, ctx:frameQLParser.TransactionStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#replicationStatement.
    def enterReplicationStatement(self, ctx:frameQLParser.ReplicationStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#replicationStatement.
    def exitReplicationStatement(self, ctx:frameQLParser.ReplicationStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#preparedStatement.
    def enterPreparedStatement(self, ctx:frameQLParser.PreparedStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#preparedStatement.
    def exitPreparedStatement(self, ctx:frameQLParser.PreparedStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#compoundStatement.
    def enterCompoundStatement(self, ctx:frameQLParser.CompoundStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#compoundStatement.
    def exitCompoundStatement(self, ctx:frameQLParser.CompoundStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#administrationStatement.
    def enterAdministrationStatement(self, ctx:frameQLParser.AdministrationStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#administrationStatement.
    def exitAdministrationStatement(self, ctx:frameQLParser.AdministrationStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#utilityStatement.
    def enterUtilityStatement(self, ctx:frameQLParser.UtilityStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#utilityStatement.
    def exitUtilityStatement(self, ctx:frameQLParser.UtilityStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#createDatabase.
    def enterCreateDatabase(self, ctx:frameQLParser.CreateDatabaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#createDatabase.
    def exitCreateDatabase(self, ctx:frameQLParser.CreateDatabaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#createEvent.
    def enterCreateEvent(self, ctx:frameQLParser.CreateEventContext):
        pass

    # Exit a parse tree produced by frameQLParser#createEvent.
    def exitCreateEvent(self, ctx:frameQLParser.CreateEventContext):
        pass


    # Enter a parse tree produced by frameQLParser#createIndex.
    def enterCreateIndex(self, ctx:frameQLParser.CreateIndexContext):
        pass

    # Exit a parse tree produced by frameQLParser#createIndex.
    def exitCreateIndex(self, ctx:frameQLParser.CreateIndexContext):
        pass


    # Enter a parse tree produced by frameQLParser#createLogfileGroup.
    def enterCreateLogfileGroup(self, ctx:frameQLParser.CreateLogfileGroupContext):
        pass

    # Exit a parse tree produced by frameQLParser#createLogfileGroup.
    def exitCreateLogfileGroup(self, ctx:frameQLParser.CreateLogfileGroupContext):
        pass


    # Enter a parse tree produced by frameQLParser#createProcedure.
    def enterCreateProcedure(self, ctx:frameQLParser.CreateProcedureContext):
        pass

    # Exit a parse tree produced by frameQLParser#createProcedure.
    def exitCreateProcedure(self, ctx:frameQLParser.CreateProcedureContext):
        pass


    # Enter a parse tree produced by frameQLParser#createFunction.
    def enterCreateFunction(self, ctx:frameQLParser.CreateFunctionContext):
        pass

    # Exit a parse tree produced by frameQLParser#createFunction.
    def exitCreateFunction(self, ctx:frameQLParser.CreateFunctionContext):
        pass


    # Enter a parse tree produced by frameQLParser#createServer.
    def enterCreateServer(self, ctx:frameQLParser.CreateServerContext):
        pass

    # Exit a parse tree produced by frameQLParser#createServer.
    def exitCreateServer(self, ctx:frameQLParser.CreateServerContext):
        pass


    # Enter a parse tree produced by frameQLParser#copyCreateTable.
    def enterCopyCreateTable(self, ctx:frameQLParser.CopyCreateTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#copyCreateTable.
    def exitCopyCreateTable(self, ctx:frameQLParser.CopyCreateTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#queryCreateTable.
    def enterQueryCreateTable(self, ctx:frameQLParser.QueryCreateTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#queryCreateTable.
    def exitQueryCreateTable(self, ctx:frameQLParser.QueryCreateTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#columnCreateTable.
    def enterColumnCreateTable(self, ctx:frameQLParser.ColumnCreateTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#columnCreateTable.
    def exitColumnCreateTable(self, ctx:frameQLParser.ColumnCreateTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#createTablespaceInnodb.
    def enterCreateTablespaceInnodb(self, ctx:frameQLParser.CreateTablespaceInnodbContext):
        pass

    # Exit a parse tree produced by frameQLParser#createTablespaceInnodb.
    def exitCreateTablespaceInnodb(self, ctx:frameQLParser.CreateTablespaceInnodbContext):
        pass


    # Enter a parse tree produced by frameQLParser#createTablespaceNdb.
    def enterCreateTablespaceNdb(self, ctx:frameQLParser.CreateTablespaceNdbContext):
        pass

    # Exit a parse tree produced by frameQLParser#createTablespaceNdb.
    def exitCreateTablespaceNdb(self, ctx:frameQLParser.CreateTablespaceNdbContext):
        pass


    # Enter a parse tree produced by frameQLParser#createTrigger.
    def enterCreateTrigger(self, ctx:frameQLParser.CreateTriggerContext):
        pass

    # Exit a parse tree produced by frameQLParser#createTrigger.
    def exitCreateTrigger(self, ctx:frameQLParser.CreateTriggerContext):
        pass


    # Enter a parse tree produced by frameQLParser#createView.
    def enterCreateView(self, ctx:frameQLParser.CreateViewContext):
        pass

    # Exit a parse tree produced by frameQLParser#createView.
    def exitCreateView(self, ctx:frameQLParser.CreateViewContext):
        pass


    # Enter a parse tree produced by frameQLParser#createDatabaseOption.
    def enterCreateDatabaseOption(self, ctx:frameQLParser.CreateDatabaseOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#createDatabaseOption.
    def exitCreateDatabaseOption(self, ctx:frameQLParser.CreateDatabaseOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#ownerStatement.
    def enterOwnerStatement(self, ctx:frameQLParser.OwnerStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#ownerStatement.
    def exitOwnerStatement(self, ctx:frameQLParser.OwnerStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#preciseSchedule.
    def enterPreciseSchedule(self, ctx:frameQLParser.PreciseScheduleContext):
        pass

    # Exit a parse tree produced by frameQLParser#preciseSchedule.
    def exitPreciseSchedule(self, ctx:frameQLParser.PreciseScheduleContext):
        pass


    # Enter a parse tree produced by frameQLParser#intervalSchedule.
    def enterIntervalSchedule(self, ctx:frameQLParser.IntervalScheduleContext):
        pass

    # Exit a parse tree produced by frameQLParser#intervalSchedule.
    def exitIntervalSchedule(self, ctx:frameQLParser.IntervalScheduleContext):
        pass


    # Enter a parse tree produced by frameQLParser#timestampValue.
    def enterTimestampValue(self, ctx:frameQLParser.TimestampValueContext):
        pass

    # Exit a parse tree produced by frameQLParser#timestampValue.
    def exitTimestampValue(self, ctx:frameQLParser.TimestampValueContext):
        pass


    # Enter a parse tree produced by frameQLParser#intervalExpr.
    def enterIntervalExpr(self, ctx:frameQLParser.IntervalExprContext):
        pass

    # Exit a parse tree produced by frameQLParser#intervalExpr.
    def exitIntervalExpr(self, ctx:frameQLParser.IntervalExprContext):
        pass


    # Enter a parse tree produced by frameQLParser#intervalType.
    def enterIntervalType(self, ctx:frameQLParser.IntervalTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#intervalType.
    def exitIntervalType(self, ctx:frameQLParser.IntervalTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#enableType.
    def enterEnableType(self, ctx:frameQLParser.EnableTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#enableType.
    def exitEnableType(self, ctx:frameQLParser.EnableTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexType.
    def enterIndexType(self, ctx:frameQLParser.IndexTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexType.
    def exitIndexType(self, ctx:frameQLParser.IndexTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexOption.
    def enterIndexOption(self, ctx:frameQLParser.IndexOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexOption.
    def exitIndexOption(self, ctx:frameQLParser.IndexOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#procedureParameter.
    def enterProcedureParameter(self, ctx:frameQLParser.ProcedureParameterContext):
        pass

    # Exit a parse tree produced by frameQLParser#procedureParameter.
    def exitProcedureParameter(self, ctx:frameQLParser.ProcedureParameterContext):
        pass


    # Enter a parse tree produced by frameQLParser#functionParameter.
    def enterFunctionParameter(self, ctx:frameQLParser.FunctionParameterContext):
        pass

    # Exit a parse tree produced by frameQLParser#functionParameter.
    def exitFunctionParameter(self, ctx:frameQLParser.FunctionParameterContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineComment.
    def enterRoutineComment(self, ctx:frameQLParser.RoutineCommentContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineComment.
    def exitRoutineComment(self, ctx:frameQLParser.RoutineCommentContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineLanguage.
    def enterRoutineLanguage(self, ctx:frameQLParser.RoutineLanguageContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineLanguage.
    def exitRoutineLanguage(self, ctx:frameQLParser.RoutineLanguageContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineBehavior.
    def enterRoutineBehavior(self, ctx:frameQLParser.RoutineBehaviorContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineBehavior.
    def exitRoutineBehavior(self, ctx:frameQLParser.RoutineBehaviorContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineData.
    def enterRoutineData(self, ctx:frameQLParser.RoutineDataContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineData.
    def exitRoutineData(self, ctx:frameQLParser.RoutineDataContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineSecurity.
    def enterRoutineSecurity(self, ctx:frameQLParser.RoutineSecurityContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineSecurity.
    def exitRoutineSecurity(self, ctx:frameQLParser.RoutineSecurityContext):
        pass


    # Enter a parse tree produced by frameQLParser#serverOption.
    def enterServerOption(self, ctx:frameQLParser.ServerOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#serverOption.
    def exitServerOption(self, ctx:frameQLParser.ServerOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#createDefinitions.
    def enterCreateDefinitions(self, ctx:frameQLParser.CreateDefinitionsContext):
        pass

    # Exit a parse tree produced by frameQLParser#createDefinitions.
    def exitCreateDefinitions(self, ctx:frameQLParser.CreateDefinitionsContext):
        pass


    # Enter a parse tree produced by frameQLParser#columnDeclaration.
    def enterColumnDeclaration(self, ctx:frameQLParser.ColumnDeclarationContext):
        pass

    # Exit a parse tree produced by frameQLParser#columnDeclaration.
    def exitColumnDeclaration(self, ctx:frameQLParser.ColumnDeclarationContext):
        pass


    # Enter a parse tree produced by frameQLParser#constraintDeclaration.
    def enterConstraintDeclaration(self, ctx:frameQLParser.ConstraintDeclarationContext):
        pass

    # Exit a parse tree produced by frameQLParser#constraintDeclaration.
    def exitConstraintDeclaration(self, ctx:frameQLParser.ConstraintDeclarationContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexDeclaration.
    def enterIndexDeclaration(self, ctx:frameQLParser.IndexDeclarationContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexDeclaration.
    def exitIndexDeclaration(self, ctx:frameQLParser.IndexDeclarationContext):
        pass


    # Enter a parse tree produced by frameQLParser#columnDefinition.
    def enterColumnDefinition(self, ctx:frameQLParser.ColumnDefinitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#columnDefinition.
    def exitColumnDefinition(self, ctx:frameQLParser.ColumnDefinitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#nullColumnConstraint.
    def enterNullColumnConstraint(self, ctx:frameQLParser.NullColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#nullColumnConstraint.
    def exitNullColumnConstraint(self, ctx:frameQLParser.NullColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#defaultColumnConstraint.
    def enterDefaultColumnConstraint(self, ctx:frameQLParser.DefaultColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#defaultColumnConstraint.
    def exitDefaultColumnConstraint(self, ctx:frameQLParser.DefaultColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#autoIncrementColumnConstraint.
    def enterAutoIncrementColumnConstraint(self, ctx:frameQLParser.AutoIncrementColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#autoIncrementColumnConstraint.
    def exitAutoIncrementColumnConstraint(self, ctx:frameQLParser.AutoIncrementColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#primaryKeyColumnConstraint.
    def enterPrimaryKeyColumnConstraint(self, ctx:frameQLParser.PrimaryKeyColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#primaryKeyColumnConstraint.
    def exitPrimaryKeyColumnConstraint(self, ctx:frameQLParser.PrimaryKeyColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#uniqueKeyColumnConstraint.
    def enterUniqueKeyColumnConstraint(self, ctx:frameQLParser.UniqueKeyColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#uniqueKeyColumnConstraint.
    def exitUniqueKeyColumnConstraint(self, ctx:frameQLParser.UniqueKeyColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#commentColumnConstraint.
    def enterCommentColumnConstraint(self, ctx:frameQLParser.CommentColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#commentColumnConstraint.
    def exitCommentColumnConstraint(self, ctx:frameQLParser.CommentColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#formatColumnConstraint.
    def enterFormatColumnConstraint(self, ctx:frameQLParser.FormatColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#formatColumnConstraint.
    def exitFormatColumnConstraint(self, ctx:frameQLParser.FormatColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#storageColumnConstraint.
    def enterStorageColumnConstraint(self, ctx:frameQLParser.StorageColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#storageColumnConstraint.
    def exitStorageColumnConstraint(self, ctx:frameQLParser.StorageColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#referenceColumnConstraint.
    def enterReferenceColumnConstraint(self, ctx:frameQLParser.ReferenceColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#referenceColumnConstraint.
    def exitReferenceColumnConstraint(self, ctx:frameQLParser.ReferenceColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#generatedColumnConstraint.
    def enterGeneratedColumnConstraint(self, ctx:frameQLParser.GeneratedColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#generatedColumnConstraint.
    def exitGeneratedColumnConstraint(self, ctx:frameQLParser.GeneratedColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#serialDefaultColumnConstraint.
    def enterSerialDefaultColumnConstraint(self, ctx:frameQLParser.SerialDefaultColumnConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#serialDefaultColumnConstraint.
    def exitSerialDefaultColumnConstraint(self, ctx:frameQLParser.SerialDefaultColumnConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#primaryKeyTableConstraint.
    def enterPrimaryKeyTableConstraint(self, ctx:frameQLParser.PrimaryKeyTableConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#primaryKeyTableConstraint.
    def exitPrimaryKeyTableConstraint(self, ctx:frameQLParser.PrimaryKeyTableConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#uniqueKeyTableConstraint.
    def enterUniqueKeyTableConstraint(self, ctx:frameQLParser.UniqueKeyTableConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#uniqueKeyTableConstraint.
    def exitUniqueKeyTableConstraint(self, ctx:frameQLParser.UniqueKeyTableConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#foreignKeyTableConstraint.
    def enterForeignKeyTableConstraint(self, ctx:frameQLParser.ForeignKeyTableConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#foreignKeyTableConstraint.
    def exitForeignKeyTableConstraint(self, ctx:frameQLParser.ForeignKeyTableConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#checkTableConstraint.
    def enterCheckTableConstraint(self, ctx:frameQLParser.CheckTableConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#checkTableConstraint.
    def exitCheckTableConstraint(self, ctx:frameQLParser.CheckTableConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#referenceDefinition.
    def enterReferenceDefinition(self, ctx:frameQLParser.ReferenceDefinitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#referenceDefinition.
    def exitReferenceDefinition(self, ctx:frameQLParser.ReferenceDefinitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#referenceAction.
    def enterReferenceAction(self, ctx:frameQLParser.ReferenceActionContext):
        pass

    # Exit a parse tree produced by frameQLParser#referenceAction.
    def exitReferenceAction(self, ctx:frameQLParser.ReferenceActionContext):
        pass


    # Enter a parse tree produced by frameQLParser#referenceControlType.
    def enterReferenceControlType(self, ctx:frameQLParser.ReferenceControlTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#referenceControlType.
    def exitReferenceControlType(self, ctx:frameQLParser.ReferenceControlTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleIndexDeclaration.
    def enterSimpleIndexDeclaration(self, ctx:frameQLParser.SimpleIndexDeclarationContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleIndexDeclaration.
    def exitSimpleIndexDeclaration(self, ctx:frameQLParser.SimpleIndexDeclarationContext):
        pass


    # Enter a parse tree produced by frameQLParser#specialIndexDeclaration.
    def enterSpecialIndexDeclaration(self, ctx:frameQLParser.SpecialIndexDeclarationContext):
        pass

    # Exit a parse tree produced by frameQLParser#specialIndexDeclaration.
    def exitSpecialIndexDeclaration(self, ctx:frameQLParser.SpecialIndexDeclarationContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionEngine.
    def enterTableOptionEngine(self, ctx:frameQLParser.TableOptionEngineContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionEngine.
    def exitTableOptionEngine(self, ctx:frameQLParser.TableOptionEngineContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionAutoIncrement.
    def enterTableOptionAutoIncrement(self, ctx:frameQLParser.TableOptionAutoIncrementContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionAutoIncrement.
    def exitTableOptionAutoIncrement(self, ctx:frameQLParser.TableOptionAutoIncrementContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionAverage.
    def enterTableOptionAverage(self, ctx:frameQLParser.TableOptionAverageContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionAverage.
    def exitTableOptionAverage(self, ctx:frameQLParser.TableOptionAverageContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionCharset.
    def enterTableOptionCharset(self, ctx:frameQLParser.TableOptionCharsetContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionCharset.
    def exitTableOptionCharset(self, ctx:frameQLParser.TableOptionCharsetContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionChecksum.
    def enterTableOptionChecksum(self, ctx:frameQLParser.TableOptionChecksumContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionChecksum.
    def exitTableOptionChecksum(self, ctx:frameQLParser.TableOptionChecksumContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionCollate.
    def enterTableOptionCollate(self, ctx:frameQLParser.TableOptionCollateContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionCollate.
    def exitTableOptionCollate(self, ctx:frameQLParser.TableOptionCollateContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionComment.
    def enterTableOptionComment(self, ctx:frameQLParser.TableOptionCommentContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionComment.
    def exitTableOptionComment(self, ctx:frameQLParser.TableOptionCommentContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionCompression.
    def enterTableOptionCompression(self, ctx:frameQLParser.TableOptionCompressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionCompression.
    def exitTableOptionCompression(self, ctx:frameQLParser.TableOptionCompressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionConnection.
    def enterTableOptionConnection(self, ctx:frameQLParser.TableOptionConnectionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionConnection.
    def exitTableOptionConnection(self, ctx:frameQLParser.TableOptionConnectionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionDataDirectory.
    def enterTableOptionDataDirectory(self, ctx:frameQLParser.TableOptionDataDirectoryContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionDataDirectory.
    def exitTableOptionDataDirectory(self, ctx:frameQLParser.TableOptionDataDirectoryContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionDelay.
    def enterTableOptionDelay(self, ctx:frameQLParser.TableOptionDelayContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionDelay.
    def exitTableOptionDelay(self, ctx:frameQLParser.TableOptionDelayContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionEncryption.
    def enterTableOptionEncryption(self, ctx:frameQLParser.TableOptionEncryptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionEncryption.
    def exitTableOptionEncryption(self, ctx:frameQLParser.TableOptionEncryptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionIndexDirectory.
    def enterTableOptionIndexDirectory(self, ctx:frameQLParser.TableOptionIndexDirectoryContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionIndexDirectory.
    def exitTableOptionIndexDirectory(self, ctx:frameQLParser.TableOptionIndexDirectoryContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionInsertMethod.
    def enterTableOptionInsertMethod(self, ctx:frameQLParser.TableOptionInsertMethodContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionInsertMethod.
    def exitTableOptionInsertMethod(self, ctx:frameQLParser.TableOptionInsertMethodContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionKeyBlockSize.
    def enterTableOptionKeyBlockSize(self, ctx:frameQLParser.TableOptionKeyBlockSizeContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionKeyBlockSize.
    def exitTableOptionKeyBlockSize(self, ctx:frameQLParser.TableOptionKeyBlockSizeContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionMaxRows.
    def enterTableOptionMaxRows(self, ctx:frameQLParser.TableOptionMaxRowsContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionMaxRows.
    def exitTableOptionMaxRows(self, ctx:frameQLParser.TableOptionMaxRowsContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionMinRows.
    def enterTableOptionMinRows(self, ctx:frameQLParser.TableOptionMinRowsContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionMinRows.
    def exitTableOptionMinRows(self, ctx:frameQLParser.TableOptionMinRowsContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionPackKeys.
    def enterTableOptionPackKeys(self, ctx:frameQLParser.TableOptionPackKeysContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionPackKeys.
    def exitTableOptionPackKeys(self, ctx:frameQLParser.TableOptionPackKeysContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionPassword.
    def enterTableOptionPassword(self, ctx:frameQLParser.TableOptionPasswordContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionPassword.
    def exitTableOptionPassword(self, ctx:frameQLParser.TableOptionPasswordContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionRowFormat.
    def enterTableOptionRowFormat(self, ctx:frameQLParser.TableOptionRowFormatContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionRowFormat.
    def exitTableOptionRowFormat(self, ctx:frameQLParser.TableOptionRowFormatContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionRecalculation.
    def enterTableOptionRecalculation(self, ctx:frameQLParser.TableOptionRecalculationContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionRecalculation.
    def exitTableOptionRecalculation(self, ctx:frameQLParser.TableOptionRecalculationContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionPersistent.
    def enterTableOptionPersistent(self, ctx:frameQLParser.TableOptionPersistentContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionPersistent.
    def exitTableOptionPersistent(self, ctx:frameQLParser.TableOptionPersistentContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionSamplePage.
    def enterTableOptionSamplePage(self, ctx:frameQLParser.TableOptionSamplePageContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionSamplePage.
    def exitTableOptionSamplePage(self, ctx:frameQLParser.TableOptionSamplePageContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionTablespace.
    def enterTableOptionTablespace(self, ctx:frameQLParser.TableOptionTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionTablespace.
    def exitTableOptionTablespace(self, ctx:frameQLParser.TableOptionTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableOptionUnion.
    def enterTableOptionUnion(self, ctx:frameQLParser.TableOptionUnionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableOptionUnion.
    def exitTableOptionUnion(self, ctx:frameQLParser.TableOptionUnionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tablespaceStorage.
    def enterTablespaceStorage(self, ctx:frameQLParser.TablespaceStorageContext):
        pass

    # Exit a parse tree produced by frameQLParser#tablespaceStorage.
    def exitTablespaceStorage(self, ctx:frameQLParser.TablespaceStorageContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionDefinitions.
    def enterPartitionDefinitions(self, ctx:frameQLParser.PartitionDefinitionsContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionDefinitions.
    def exitPartitionDefinitions(self, ctx:frameQLParser.PartitionDefinitionsContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionFunctionHash.
    def enterPartitionFunctionHash(self, ctx:frameQLParser.PartitionFunctionHashContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionFunctionHash.
    def exitPartitionFunctionHash(self, ctx:frameQLParser.PartitionFunctionHashContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionFunctionKey.
    def enterPartitionFunctionKey(self, ctx:frameQLParser.PartitionFunctionKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionFunctionKey.
    def exitPartitionFunctionKey(self, ctx:frameQLParser.PartitionFunctionKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionFunctionRange.
    def enterPartitionFunctionRange(self, ctx:frameQLParser.PartitionFunctionRangeContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionFunctionRange.
    def exitPartitionFunctionRange(self, ctx:frameQLParser.PartitionFunctionRangeContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionFunctionList.
    def enterPartitionFunctionList(self, ctx:frameQLParser.PartitionFunctionListContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionFunctionList.
    def exitPartitionFunctionList(self, ctx:frameQLParser.PartitionFunctionListContext):
        pass


    # Enter a parse tree produced by frameQLParser#subPartitionFunctionHash.
    def enterSubPartitionFunctionHash(self, ctx:frameQLParser.SubPartitionFunctionHashContext):
        pass

    # Exit a parse tree produced by frameQLParser#subPartitionFunctionHash.
    def exitSubPartitionFunctionHash(self, ctx:frameQLParser.SubPartitionFunctionHashContext):
        pass


    # Enter a parse tree produced by frameQLParser#subPartitionFunctionKey.
    def enterSubPartitionFunctionKey(self, ctx:frameQLParser.SubPartitionFunctionKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#subPartitionFunctionKey.
    def exitSubPartitionFunctionKey(self, ctx:frameQLParser.SubPartitionFunctionKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionComparision.
    def enterPartitionComparision(self, ctx:frameQLParser.PartitionComparisionContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionComparision.
    def exitPartitionComparision(self, ctx:frameQLParser.PartitionComparisionContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionListAtom.
    def enterPartitionListAtom(self, ctx:frameQLParser.PartitionListAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionListAtom.
    def exitPartitionListAtom(self, ctx:frameQLParser.PartitionListAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionListVector.
    def enterPartitionListVector(self, ctx:frameQLParser.PartitionListVectorContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionListVector.
    def exitPartitionListVector(self, ctx:frameQLParser.PartitionListVectorContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionSimple.
    def enterPartitionSimple(self, ctx:frameQLParser.PartitionSimpleContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionSimple.
    def exitPartitionSimple(self, ctx:frameQLParser.PartitionSimpleContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionDefinerAtom.
    def enterPartitionDefinerAtom(self, ctx:frameQLParser.PartitionDefinerAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionDefinerAtom.
    def exitPartitionDefinerAtom(self, ctx:frameQLParser.PartitionDefinerAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionDefinerVector.
    def enterPartitionDefinerVector(self, ctx:frameQLParser.PartitionDefinerVectorContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionDefinerVector.
    def exitPartitionDefinerVector(self, ctx:frameQLParser.PartitionDefinerVectorContext):
        pass


    # Enter a parse tree produced by frameQLParser#subpartitionDefinition.
    def enterSubpartitionDefinition(self, ctx:frameQLParser.SubpartitionDefinitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#subpartitionDefinition.
    def exitSubpartitionDefinition(self, ctx:frameQLParser.SubpartitionDefinitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionEngine.
    def enterPartitionOptionEngine(self, ctx:frameQLParser.PartitionOptionEngineContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionEngine.
    def exitPartitionOptionEngine(self, ctx:frameQLParser.PartitionOptionEngineContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionComment.
    def enterPartitionOptionComment(self, ctx:frameQLParser.PartitionOptionCommentContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionComment.
    def exitPartitionOptionComment(self, ctx:frameQLParser.PartitionOptionCommentContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionDataDirectory.
    def enterPartitionOptionDataDirectory(self, ctx:frameQLParser.PartitionOptionDataDirectoryContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionDataDirectory.
    def exitPartitionOptionDataDirectory(self, ctx:frameQLParser.PartitionOptionDataDirectoryContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionIndexDirectory.
    def enterPartitionOptionIndexDirectory(self, ctx:frameQLParser.PartitionOptionIndexDirectoryContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionIndexDirectory.
    def exitPartitionOptionIndexDirectory(self, ctx:frameQLParser.PartitionOptionIndexDirectoryContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionMaxRows.
    def enterPartitionOptionMaxRows(self, ctx:frameQLParser.PartitionOptionMaxRowsContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionMaxRows.
    def exitPartitionOptionMaxRows(self, ctx:frameQLParser.PartitionOptionMaxRowsContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionMinRows.
    def enterPartitionOptionMinRows(self, ctx:frameQLParser.PartitionOptionMinRowsContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionMinRows.
    def exitPartitionOptionMinRows(self, ctx:frameQLParser.PartitionOptionMinRowsContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionTablespace.
    def enterPartitionOptionTablespace(self, ctx:frameQLParser.PartitionOptionTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionTablespace.
    def exitPartitionOptionTablespace(self, ctx:frameQLParser.PartitionOptionTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#partitionOptionNodeGroup.
    def enterPartitionOptionNodeGroup(self, ctx:frameQLParser.PartitionOptionNodeGroupContext):
        pass

    # Exit a parse tree produced by frameQLParser#partitionOptionNodeGroup.
    def exitPartitionOptionNodeGroup(self, ctx:frameQLParser.PartitionOptionNodeGroupContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterSimpleDatabase.
    def enterAlterSimpleDatabase(self, ctx:frameQLParser.AlterSimpleDatabaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterSimpleDatabase.
    def exitAlterSimpleDatabase(self, ctx:frameQLParser.AlterSimpleDatabaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterUpgradeName.
    def enterAlterUpgradeName(self, ctx:frameQLParser.AlterUpgradeNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterUpgradeName.
    def exitAlterUpgradeName(self, ctx:frameQLParser.AlterUpgradeNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterEvent.
    def enterAlterEvent(self, ctx:frameQLParser.AlterEventContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterEvent.
    def exitAlterEvent(self, ctx:frameQLParser.AlterEventContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterFunction.
    def enterAlterFunction(self, ctx:frameQLParser.AlterFunctionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterFunction.
    def exitAlterFunction(self, ctx:frameQLParser.AlterFunctionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterInstance.
    def enterAlterInstance(self, ctx:frameQLParser.AlterInstanceContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterInstance.
    def exitAlterInstance(self, ctx:frameQLParser.AlterInstanceContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterLogfileGroup.
    def enterAlterLogfileGroup(self, ctx:frameQLParser.AlterLogfileGroupContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterLogfileGroup.
    def exitAlterLogfileGroup(self, ctx:frameQLParser.AlterLogfileGroupContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterProcedure.
    def enterAlterProcedure(self, ctx:frameQLParser.AlterProcedureContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterProcedure.
    def exitAlterProcedure(self, ctx:frameQLParser.AlterProcedureContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterServer.
    def enterAlterServer(self, ctx:frameQLParser.AlterServerContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterServer.
    def exitAlterServer(self, ctx:frameQLParser.AlterServerContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterTable.
    def enterAlterTable(self, ctx:frameQLParser.AlterTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterTable.
    def exitAlterTable(self, ctx:frameQLParser.AlterTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterTablespace.
    def enterAlterTablespace(self, ctx:frameQLParser.AlterTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterTablespace.
    def exitAlterTablespace(self, ctx:frameQLParser.AlterTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterView.
    def enterAlterView(self, ctx:frameQLParser.AlterViewContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterView.
    def exitAlterView(self, ctx:frameQLParser.AlterViewContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByTableOption.
    def enterAlterByTableOption(self, ctx:frameQLParser.AlterByTableOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByTableOption.
    def exitAlterByTableOption(self, ctx:frameQLParser.AlterByTableOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddColumn.
    def enterAlterByAddColumn(self, ctx:frameQLParser.AlterByAddColumnContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddColumn.
    def exitAlterByAddColumn(self, ctx:frameQLParser.AlterByAddColumnContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddColumns.
    def enterAlterByAddColumns(self, ctx:frameQLParser.AlterByAddColumnsContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddColumns.
    def exitAlterByAddColumns(self, ctx:frameQLParser.AlterByAddColumnsContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddIndex.
    def enterAlterByAddIndex(self, ctx:frameQLParser.AlterByAddIndexContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddIndex.
    def exitAlterByAddIndex(self, ctx:frameQLParser.AlterByAddIndexContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddPrimaryKey.
    def enterAlterByAddPrimaryKey(self, ctx:frameQLParser.AlterByAddPrimaryKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddPrimaryKey.
    def exitAlterByAddPrimaryKey(self, ctx:frameQLParser.AlterByAddPrimaryKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddUniqueKey.
    def enterAlterByAddUniqueKey(self, ctx:frameQLParser.AlterByAddUniqueKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddUniqueKey.
    def exitAlterByAddUniqueKey(self, ctx:frameQLParser.AlterByAddUniqueKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddSpecialIndex.
    def enterAlterByAddSpecialIndex(self, ctx:frameQLParser.AlterByAddSpecialIndexContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddSpecialIndex.
    def exitAlterByAddSpecialIndex(self, ctx:frameQLParser.AlterByAddSpecialIndexContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddForeignKey.
    def enterAlterByAddForeignKey(self, ctx:frameQLParser.AlterByAddForeignKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddForeignKey.
    def exitAlterByAddForeignKey(self, ctx:frameQLParser.AlterByAddForeignKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddCheckTableConstraint.
    def enterAlterByAddCheckTableConstraint(self, ctx:frameQLParser.AlterByAddCheckTableConstraintContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddCheckTableConstraint.
    def exitAlterByAddCheckTableConstraint(self, ctx:frameQLParser.AlterByAddCheckTableConstraintContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterBySetAlgorithm.
    def enterAlterBySetAlgorithm(self, ctx:frameQLParser.AlterBySetAlgorithmContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterBySetAlgorithm.
    def exitAlterBySetAlgorithm(self, ctx:frameQLParser.AlterBySetAlgorithmContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByChangeDefault.
    def enterAlterByChangeDefault(self, ctx:frameQLParser.AlterByChangeDefaultContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByChangeDefault.
    def exitAlterByChangeDefault(self, ctx:frameQLParser.AlterByChangeDefaultContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByChangeColumn.
    def enterAlterByChangeColumn(self, ctx:frameQLParser.AlterByChangeColumnContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByChangeColumn.
    def exitAlterByChangeColumn(self, ctx:frameQLParser.AlterByChangeColumnContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByRenameColumn.
    def enterAlterByRenameColumn(self, ctx:frameQLParser.AlterByRenameColumnContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByRenameColumn.
    def exitAlterByRenameColumn(self, ctx:frameQLParser.AlterByRenameColumnContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByLock.
    def enterAlterByLock(self, ctx:frameQLParser.AlterByLockContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByLock.
    def exitAlterByLock(self, ctx:frameQLParser.AlterByLockContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByModifyColumn.
    def enterAlterByModifyColumn(self, ctx:frameQLParser.AlterByModifyColumnContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByModifyColumn.
    def exitAlterByModifyColumn(self, ctx:frameQLParser.AlterByModifyColumnContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDropColumn.
    def enterAlterByDropColumn(self, ctx:frameQLParser.AlterByDropColumnContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDropColumn.
    def exitAlterByDropColumn(self, ctx:frameQLParser.AlterByDropColumnContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDropPrimaryKey.
    def enterAlterByDropPrimaryKey(self, ctx:frameQLParser.AlterByDropPrimaryKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDropPrimaryKey.
    def exitAlterByDropPrimaryKey(self, ctx:frameQLParser.AlterByDropPrimaryKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDropIndex.
    def enterAlterByDropIndex(self, ctx:frameQLParser.AlterByDropIndexContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDropIndex.
    def exitAlterByDropIndex(self, ctx:frameQLParser.AlterByDropIndexContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDropForeignKey.
    def enterAlterByDropForeignKey(self, ctx:frameQLParser.AlterByDropForeignKeyContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDropForeignKey.
    def exitAlterByDropForeignKey(self, ctx:frameQLParser.AlterByDropForeignKeyContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDisableKeys.
    def enterAlterByDisableKeys(self, ctx:frameQLParser.AlterByDisableKeysContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDisableKeys.
    def exitAlterByDisableKeys(self, ctx:frameQLParser.AlterByDisableKeysContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByEnableKeys.
    def enterAlterByEnableKeys(self, ctx:frameQLParser.AlterByEnableKeysContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByEnableKeys.
    def exitAlterByEnableKeys(self, ctx:frameQLParser.AlterByEnableKeysContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByRename.
    def enterAlterByRename(self, ctx:frameQLParser.AlterByRenameContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByRename.
    def exitAlterByRename(self, ctx:frameQLParser.AlterByRenameContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByOrder.
    def enterAlterByOrder(self, ctx:frameQLParser.AlterByOrderContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByOrder.
    def exitAlterByOrder(self, ctx:frameQLParser.AlterByOrderContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByConvertCharset.
    def enterAlterByConvertCharset(self, ctx:frameQLParser.AlterByConvertCharsetContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByConvertCharset.
    def exitAlterByConvertCharset(self, ctx:frameQLParser.AlterByConvertCharsetContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDefaultCharset.
    def enterAlterByDefaultCharset(self, ctx:frameQLParser.AlterByDefaultCharsetContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDefaultCharset.
    def exitAlterByDefaultCharset(self, ctx:frameQLParser.AlterByDefaultCharsetContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDiscardTablespace.
    def enterAlterByDiscardTablespace(self, ctx:frameQLParser.AlterByDiscardTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDiscardTablespace.
    def exitAlterByDiscardTablespace(self, ctx:frameQLParser.AlterByDiscardTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByImportTablespace.
    def enterAlterByImportTablespace(self, ctx:frameQLParser.AlterByImportTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByImportTablespace.
    def exitAlterByImportTablespace(self, ctx:frameQLParser.AlterByImportTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByForce.
    def enterAlterByForce(self, ctx:frameQLParser.AlterByForceContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByForce.
    def exitAlterByForce(self, ctx:frameQLParser.AlterByForceContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByValidate.
    def enterAlterByValidate(self, ctx:frameQLParser.AlterByValidateContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByValidate.
    def exitAlterByValidate(self, ctx:frameQLParser.AlterByValidateContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAddPartition.
    def enterAlterByAddPartition(self, ctx:frameQLParser.AlterByAddPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAddPartition.
    def exitAlterByAddPartition(self, ctx:frameQLParser.AlterByAddPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDropPartition.
    def enterAlterByDropPartition(self, ctx:frameQLParser.AlterByDropPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDropPartition.
    def exitAlterByDropPartition(self, ctx:frameQLParser.AlterByDropPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByDiscardPartition.
    def enterAlterByDiscardPartition(self, ctx:frameQLParser.AlterByDiscardPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByDiscardPartition.
    def exitAlterByDiscardPartition(self, ctx:frameQLParser.AlterByDiscardPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByImportPartition.
    def enterAlterByImportPartition(self, ctx:frameQLParser.AlterByImportPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByImportPartition.
    def exitAlterByImportPartition(self, ctx:frameQLParser.AlterByImportPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByTruncatePartition.
    def enterAlterByTruncatePartition(self, ctx:frameQLParser.AlterByTruncatePartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByTruncatePartition.
    def exitAlterByTruncatePartition(self, ctx:frameQLParser.AlterByTruncatePartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByCoalescePartition.
    def enterAlterByCoalescePartition(self, ctx:frameQLParser.AlterByCoalescePartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByCoalescePartition.
    def exitAlterByCoalescePartition(self, ctx:frameQLParser.AlterByCoalescePartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByReorganizePartition.
    def enterAlterByReorganizePartition(self, ctx:frameQLParser.AlterByReorganizePartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByReorganizePartition.
    def exitAlterByReorganizePartition(self, ctx:frameQLParser.AlterByReorganizePartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByExchangePartition.
    def enterAlterByExchangePartition(self, ctx:frameQLParser.AlterByExchangePartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByExchangePartition.
    def exitAlterByExchangePartition(self, ctx:frameQLParser.AlterByExchangePartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByAnalyzePartitiion.
    def enterAlterByAnalyzePartitiion(self, ctx:frameQLParser.AlterByAnalyzePartitiionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByAnalyzePartitiion.
    def exitAlterByAnalyzePartitiion(self, ctx:frameQLParser.AlterByAnalyzePartitiionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByCheckPartition.
    def enterAlterByCheckPartition(self, ctx:frameQLParser.AlterByCheckPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByCheckPartition.
    def exitAlterByCheckPartition(self, ctx:frameQLParser.AlterByCheckPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByOptimizePartition.
    def enterAlterByOptimizePartition(self, ctx:frameQLParser.AlterByOptimizePartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByOptimizePartition.
    def exitAlterByOptimizePartition(self, ctx:frameQLParser.AlterByOptimizePartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByRebuildPartition.
    def enterAlterByRebuildPartition(self, ctx:frameQLParser.AlterByRebuildPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByRebuildPartition.
    def exitAlterByRebuildPartition(self, ctx:frameQLParser.AlterByRebuildPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByRepairPartition.
    def enterAlterByRepairPartition(self, ctx:frameQLParser.AlterByRepairPartitionContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByRepairPartition.
    def exitAlterByRepairPartition(self, ctx:frameQLParser.AlterByRepairPartitionContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByRemovePartitioning.
    def enterAlterByRemovePartitioning(self, ctx:frameQLParser.AlterByRemovePartitioningContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByRemovePartitioning.
    def exitAlterByRemovePartitioning(self, ctx:frameQLParser.AlterByRemovePartitioningContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterByUpgradePartitioning.
    def enterAlterByUpgradePartitioning(self, ctx:frameQLParser.AlterByUpgradePartitioningContext):
        pass

    # Exit a parse tree produced by frameQLParser#alterByUpgradePartitioning.
    def exitAlterByUpgradePartitioning(self, ctx:frameQLParser.AlterByUpgradePartitioningContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropDatabase.
    def enterDropDatabase(self, ctx:frameQLParser.DropDatabaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropDatabase.
    def exitDropDatabase(self, ctx:frameQLParser.DropDatabaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropEvent.
    def enterDropEvent(self, ctx:frameQLParser.DropEventContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropEvent.
    def exitDropEvent(self, ctx:frameQLParser.DropEventContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropIndex.
    def enterDropIndex(self, ctx:frameQLParser.DropIndexContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropIndex.
    def exitDropIndex(self, ctx:frameQLParser.DropIndexContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropLogfileGroup.
    def enterDropLogfileGroup(self, ctx:frameQLParser.DropLogfileGroupContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropLogfileGroup.
    def exitDropLogfileGroup(self, ctx:frameQLParser.DropLogfileGroupContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropProcedure.
    def enterDropProcedure(self, ctx:frameQLParser.DropProcedureContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropProcedure.
    def exitDropProcedure(self, ctx:frameQLParser.DropProcedureContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropFunction.
    def enterDropFunction(self, ctx:frameQLParser.DropFunctionContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropFunction.
    def exitDropFunction(self, ctx:frameQLParser.DropFunctionContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropServer.
    def enterDropServer(self, ctx:frameQLParser.DropServerContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropServer.
    def exitDropServer(self, ctx:frameQLParser.DropServerContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropTable.
    def enterDropTable(self, ctx:frameQLParser.DropTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropTable.
    def exitDropTable(self, ctx:frameQLParser.DropTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropTablespace.
    def enterDropTablespace(self, ctx:frameQLParser.DropTablespaceContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropTablespace.
    def exitDropTablespace(self, ctx:frameQLParser.DropTablespaceContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropTrigger.
    def enterDropTrigger(self, ctx:frameQLParser.DropTriggerContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropTrigger.
    def exitDropTrigger(self, ctx:frameQLParser.DropTriggerContext):
        pass


    # Enter a parse tree produced by frameQLParser#dropView.
    def enterDropView(self, ctx:frameQLParser.DropViewContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropView.
    def exitDropView(self, ctx:frameQLParser.DropViewContext):
        pass


    # Enter a parse tree produced by frameQLParser#renameTable.
    def enterRenameTable(self, ctx:frameQLParser.RenameTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#renameTable.
    def exitRenameTable(self, ctx:frameQLParser.RenameTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#renameTableClause.
    def enterRenameTableClause(self, ctx:frameQLParser.RenameTableClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#renameTableClause.
    def exitRenameTableClause(self, ctx:frameQLParser.RenameTableClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#truncateTable.
    def enterTruncateTable(self, ctx:frameQLParser.TruncateTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#truncateTable.
    def exitTruncateTable(self, ctx:frameQLParser.TruncateTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#callStatement.
    def enterCallStatement(self, ctx:frameQLParser.CallStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#callStatement.
    def exitCallStatement(self, ctx:frameQLParser.CallStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#deleteStatement.
    def enterDeleteStatement(self, ctx:frameQLParser.DeleteStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#deleteStatement.
    def exitDeleteStatement(self, ctx:frameQLParser.DeleteStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#doStatement.
    def enterDoStatement(self, ctx:frameQLParser.DoStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#doStatement.
    def exitDoStatement(self, ctx:frameQLParser.DoStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerStatement.
    def enterHandlerStatement(self, ctx:frameQLParser.HandlerStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerStatement.
    def exitHandlerStatement(self, ctx:frameQLParser.HandlerStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#insertStatement.
    def enterInsertStatement(self, ctx:frameQLParser.InsertStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#insertStatement.
    def exitInsertStatement(self, ctx:frameQLParser.InsertStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#loadDataStatement.
    def enterLoadDataStatement(self, ctx:frameQLParser.LoadDataStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#loadDataStatement.
    def exitLoadDataStatement(self, ctx:frameQLParser.LoadDataStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#loadXmlStatement.
    def enterLoadXmlStatement(self, ctx:frameQLParser.LoadXmlStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#loadXmlStatement.
    def exitLoadXmlStatement(self, ctx:frameQLParser.LoadXmlStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#replaceStatement.
    def enterReplaceStatement(self, ctx:frameQLParser.ReplaceStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#replaceStatement.
    def exitReplaceStatement(self, ctx:frameQLParser.ReplaceStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleSelect.
    def enterSimpleSelect(self, ctx:frameQLParser.SimpleSelectContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleSelect.
    def exitSimpleSelect(self, ctx:frameQLParser.SimpleSelectContext):
        pass


    # Enter a parse tree produced by frameQLParser#parenthesisSelect.
    def enterParenthesisSelect(self, ctx:frameQLParser.ParenthesisSelectContext):
        pass

    # Exit a parse tree produced by frameQLParser#parenthesisSelect.
    def exitParenthesisSelect(self, ctx:frameQLParser.ParenthesisSelectContext):
        pass


    # Enter a parse tree produced by frameQLParser#unionSelect.
    def enterUnionSelect(self, ctx:frameQLParser.UnionSelectContext):
        pass

    # Exit a parse tree produced by frameQLParser#unionSelect.
    def exitUnionSelect(self, ctx:frameQLParser.UnionSelectContext):
        pass


    # Enter a parse tree produced by frameQLParser#unionParenthesisSelect.
    def enterUnionParenthesisSelect(self, ctx:frameQLParser.UnionParenthesisSelectContext):
        pass

    # Exit a parse tree produced by frameQLParser#unionParenthesisSelect.
    def exitUnionParenthesisSelect(self, ctx:frameQLParser.UnionParenthesisSelectContext):
        pass


    # Enter a parse tree produced by frameQLParser#updateStatement.
    def enterUpdateStatement(self, ctx:frameQLParser.UpdateStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#updateStatement.
    def exitUpdateStatement(self, ctx:frameQLParser.UpdateStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#insertStatementValue.
    def enterInsertStatementValue(self, ctx:frameQLParser.InsertStatementValueContext):
        pass

    # Exit a parse tree produced by frameQLParser#insertStatementValue.
    def exitInsertStatementValue(self, ctx:frameQLParser.InsertStatementValueContext):
        pass


    # Enter a parse tree produced by frameQLParser#updatedElement.
    def enterUpdatedElement(self, ctx:frameQLParser.UpdatedElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#updatedElement.
    def exitUpdatedElement(self, ctx:frameQLParser.UpdatedElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#assignmentField.
    def enterAssignmentField(self, ctx:frameQLParser.AssignmentFieldContext):
        pass

    # Exit a parse tree produced by frameQLParser#assignmentField.
    def exitAssignmentField(self, ctx:frameQLParser.AssignmentFieldContext):
        pass


    # Enter a parse tree produced by frameQLParser#lockClause.
    def enterLockClause(self, ctx:frameQLParser.LockClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#lockClause.
    def exitLockClause(self, ctx:frameQLParser.LockClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#singleDeleteStatement.
    def enterSingleDeleteStatement(self, ctx:frameQLParser.SingleDeleteStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#singleDeleteStatement.
    def exitSingleDeleteStatement(self, ctx:frameQLParser.SingleDeleteStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#multipleDeleteStatement.
    def enterMultipleDeleteStatement(self, ctx:frameQLParser.MultipleDeleteStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#multipleDeleteStatement.
    def exitMultipleDeleteStatement(self, ctx:frameQLParser.MultipleDeleteStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerOpenStatement.
    def enterHandlerOpenStatement(self, ctx:frameQLParser.HandlerOpenStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerOpenStatement.
    def exitHandlerOpenStatement(self, ctx:frameQLParser.HandlerOpenStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerReadIndexStatement.
    def enterHandlerReadIndexStatement(self, ctx:frameQLParser.HandlerReadIndexStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerReadIndexStatement.
    def exitHandlerReadIndexStatement(self, ctx:frameQLParser.HandlerReadIndexStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerReadStatement.
    def enterHandlerReadStatement(self, ctx:frameQLParser.HandlerReadStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerReadStatement.
    def exitHandlerReadStatement(self, ctx:frameQLParser.HandlerReadStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerCloseStatement.
    def enterHandlerCloseStatement(self, ctx:frameQLParser.HandlerCloseStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerCloseStatement.
    def exitHandlerCloseStatement(self, ctx:frameQLParser.HandlerCloseStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#singleUpdateStatement.
    def enterSingleUpdateStatement(self, ctx:frameQLParser.SingleUpdateStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#singleUpdateStatement.
    def exitSingleUpdateStatement(self, ctx:frameQLParser.SingleUpdateStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#multipleUpdateStatement.
    def enterMultipleUpdateStatement(self, ctx:frameQLParser.MultipleUpdateStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#multipleUpdateStatement.
    def exitMultipleUpdateStatement(self, ctx:frameQLParser.MultipleUpdateStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#orderByClause.
    def enterOrderByClause(self, ctx:frameQLParser.OrderByClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#orderByClause.
    def exitOrderByClause(self, ctx:frameQLParser.OrderByClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#orderByExpression.
    def enterOrderByExpression(self, ctx:frameQLParser.OrderByExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#orderByExpression.
    def exitOrderByExpression(self, ctx:frameQLParser.OrderByExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableSources.
    def enterTableSources(self, ctx:frameQLParser.TableSourcesContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableSources.
    def exitTableSources(self, ctx:frameQLParser.TableSourcesContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableSourceBase.
    def enterTableSourceBase(self, ctx:frameQLParser.TableSourceBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableSourceBase.
    def exitTableSourceBase(self, ctx:frameQLParser.TableSourceBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableSourceNested.
    def enterTableSourceNested(self, ctx:frameQLParser.TableSourceNestedContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableSourceNested.
    def exitTableSourceNested(self, ctx:frameQLParser.TableSourceNestedContext):
        pass


    # Enter a parse tree produced by frameQLParser#atomTableItem.
    def enterAtomTableItem(self, ctx:frameQLParser.AtomTableItemContext):
        pass

    # Exit a parse tree produced by frameQLParser#atomTableItem.
    def exitAtomTableItem(self, ctx:frameQLParser.AtomTableItemContext):
        pass


    # Enter a parse tree produced by frameQLParser#subqueryTableItem.
    def enterSubqueryTableItem(self, ctx:frameQLParser.SubqueryTableItemContext):
        pass

    # Exit a parse tree produced by frameQLParser#subqueryTableItem.
    def exitSubqueryTableItem(self, ctx:frameQLParser.SubqueryTableItemContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableSourcesItem.
    def enterTableSourcesItem(self, ctx:frameQLParser.TableSourcesItemContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableSourcesItem.
    def exitTableSourcesItem(self, ctx:frameQLParser.TableSourcesItemContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexHint.
    def enterIndexHint(self, ctx:frameQLParser.IndexHintContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexHint.
    def exitIndexHint(self, ctx:frameQLParser.IndexHintContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexHintType.
    def enterIndexHintType(self, ctx:frameQLParser.IndexHintTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexHintType.
    def exitIndexHintType(self, ctx:frameQLParser.IndexHintTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#innerJoin.
    def enterInnerJoin(self, ctx:frameQLParser.InnerJoinContext):
        pass

    # Exit a parse tree produced by frameQLParser#innerJoin.
    def exitInnerJoin(self, ctx:frameQLParser.InnerJoinContext):
        pass


    # Enter a parse tree produced by frameQLParser#straightJoin.
    def enterStraightJoin(self, ctx:frameQLParser.StraightJoinContext):
        pass

    # Exit a parse tree produced by frameQLParser#straightJoin.
    def exitStraightJoin(self, ctx:frameQLParser.StraightJoinContext):
        pass


    # Enter a parse tree produced by frameQLParser#outerJoin.
    def enterOuterJoin(self, ctx:frameQLParser.OuterJoinContext):
        pass

    # Exit a parse tree produced by frameQLParser#outerJoin.
    def exitOuterJoin(self, ctx:frameQLParser.OuterJoinContext):
        pass


    # Enter a parse tree produced by frameQLParser#naturalJoin.
    def enterNaturalJoin(self, ctx:frameQLParser.NaturalJoinContext):
        pass

    # Exit a parse tree produced by frameQLParser#naturalJoin.
    def exitNaturalJoin(self, ctx:frameQLParser.NaturalJoinContext):
        pass


    # Enter a parse tree produced by frameQLParser#queryExpression.
    def enterQueryExpression(self, ctx:frameQLParser.QueryExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#queryExpression.
    def exitQueryExpression(self, ctx:frameQLParser.QueryExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#queryExpressionNointo.
    def enterQueryExpressionNointo(self, ctx:frameQLParser.QueryExpressionNointoContext):
        pass

    # Exit a parse tree produced by frameQLParser#queryExpressionNointo.
    def exitQueryExpressionNointo(self, ctx:frameQLParser.QueryExpressionNointoContext):
        pass


    # Enter a parse tree produced by frameQLParser#querySpecification.
    def enterQuerySpecification(self, ctx:frameQLParser.QuerySpecificationContext):
        pass

    # Exit a parse tree produced by frameQLParser#querySpecification.
    def exitQuerySpecification(self, ctx:frameQLParser.QuerySpecificationContext):
        pass


    # Enter a parse tree produced by frameQLParser#querySpecificationNointo.
    def enterQuerySpecificationNointo(self, ctx:frameQLParser.QuerySpecificationNointoContext):
        pass

    # Exit a parse tree produced by frameQLParser#querySpecificationNointo.
    def exitQuerySpecificationNointo(self, ctx:frameQLParser.QuerySpecificationNointoContext):
        pass


    # Enter a parse tree produced by frameQLParser#unionParenthesis.
    def enterUnionParenthesis(self, ctx:frameQLParser.UnionParenthesisContext):
        pass

    # Exit a parse tree produced by frameQLParser#unionParenthesis.
    def exitUnionParenthesis(self, ctx:frameQLParser.UnionParenthesisContext):
        pass


    # Enter a parse tree produced by frameQLParser#unionStatement.
    def enterUnionStatement(self, ctx:frameQLParser.UnionStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#unionStatement.
    def exitUnionStatement(self, ctx:frameQLParser.UnionStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectSpec.
    def enterSelectSpec(self, ctx:frameQLParser.SelectSpecContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectSpec.
    def exitSelectSpec(self, ctx:frameQLParser.SelectSpecContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectElements.
    def enterSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectElements.
    def exitSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectStarElement.
    def enterSelectStarElement(self, ctx:frameQLParser.SelectStarElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectStarElement.
    def exitSelectStarElement(self, ctx:frameQLParser.SelectStarElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectColumnElement.
    def enterSelectColumnElement(self, ctx:frameQLParser.SelectColumnElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectColumnElement.
    def exitSelectColumnElement(self, ctx:frameQLParser.SelectColumnElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectFunctionElement.
    def enterSelectFunctionElement(self, ctx:frameQLParser.SelectFunctionElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectFunctionElement.
    def exitSelectFunctionElement(self, ctx:frameQLParser.SelectFunctionElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectExpressionElement.
    def enterSelectExpressionElement(self, ctx:frameQLParser.SelectExpressionElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectExpressionElement.
    def exitSelectExpressionElement(self, ctx:frameQLParser.SelectExpressionElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#errorTolerenceExpression.
    def enterErrorTolerenceExpression(self, ctx:frameQLParser.ErrorTolerenceExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#errorTolerenceExpression.
    def exitErrorTolerenceExpression(self, ctx:frameQLParser.ErrorTolerenceExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#confLevelExpression.
    def enterConfLevelExpression(self, ctx:frameQLParser.ConfLevelExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#confLevelExpression.
    def exitConfLevelExpression(self, ctx:frameQLParser.ConfLevelExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectIntoVariables.
    def enterSelectIntoVariables(self, ctx:frameQLParser.SelectIntoVariablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectIntoVariables.
    def exitSelectIntoVariables(self, ctx:frameQLParser.SelectIntoVariablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectIntoDumpFile.
    def enterSelectIntoDumpFile(self, ctx:frameQLParser.SelectIntoDumpFileContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectIntoDumpFile.
    def exitSelectIntoDumpFile(self, ctx:frameQLParser.SelectIntoDumpFileContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectIntoTextFile.
    def enterSelectIntoTextFile(self, ctx:frameQLParser.SelectIntoTextFileContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectIntoTextFile.
    def exitSelectIntoTextFile(self, ctx:frameQLParser.SelectIntoTextFileContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectFieldsInto.
    def enterSelectFieldsInto(self, ctx:frameQLParser.SelectFieldsIntoContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectFieldsInto.
    def exitSelectFieldsInto(self, ctx:frameQLParser.SelectFieldsIntoContext):
        pass


    # Enter a parse tree produced by frameQLParser#selectLinesInto.
    def enterSelectLinesInto(self, ctx:frameQLParser.SelectLinesIntoContext):
        pass

    # Exit a parse tree produced by frameQLParser#selectLinesInto.
    def exitSelectLinesInto(self, ctx:frameQLParser.SelectLinesIntoContext):
        pass


    # Enter a parse tree produced by frameQLParser#fromClause.
    def enterFromClause(self, ctx:frameQLParser.FromClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#fromClause.
    def exitFromClause(self, ctx:frameQLParser.FromClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#groupByItem.
    def enterGroupByItem(self, ctx:frameQLParser.GroupByItemContext):
        pass

    # Exit a parse tree produced by frameQLParser#groupByItem.
    def exitGroupByItem(self, ctx:frameQLParser.GroupByItemContext):
        pass


    # Enter a parse tree produced by frameQLParser#limitClause.
    def enterLimitClause(self, ctx:frameQLParser.LimitClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#limitClause.
    def exitLimitClause(self, ctx:frameQLParser.LimitClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#startTransaction.
    def enterStartTransaction(self, ctx:frameQLParser.StartTransactionContext):
        pass

    # Exit a parse tree produced by frameQLParser#startTransaction.
    def exitStartTransaction(self, ctx:frameQLParser.StartTransactionContext):
        pass


    # Enter a parse tree produced by frameQLParser#beginWork.
    def enterBeginWork(self, ctx:frameQLParser.BeginWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#beginWork.
    def exitBeginWork(self, ctx:frameQLParser.BeginWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#commitWork.
    def enterCommitWork(self, ctx:frameQLParser.CommitWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#commitWork.
    def exitCommitWork(self, ctx:frameQLParser.CommitWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#rollbackWork.
    def enterRollbackWork(self, ctx:frameQLParser.RollbackWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#rollbackWork.
    def exitRollbackWork(self, ctx:frameQLParser.RollbackWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#savepointStatement.
    def enterSavepointStatement(self, ctx:frameQLParser.SavepointStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#savepointStatement.
    def exitSavepointStatement(self, ctx:frameQLParser.SavepointStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#rollbackStatement.
    def enterRollbackStatement(self, ctx:frameQLParser.RollbackStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#rollbackStatement.
    def exitRollbackStatement(self, ctx:frameQLParser.RollbackStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#releaseStatement.
    def enterReleaseStatement(self, ctx:frameQLParser.ReleaseStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#releaseStatement.
    def exitReleaseStatement(self, ctx:frameQLParser.ReleaseStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#lockTables.
    def enterLockTables(self, ctx:frameQLParser.LockTablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#lockTables.
    def exitLockTables(self, ctx:frameQLParser.LockTablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#unlockTables.
    def enterUnlockTables(self, ctx:frameQLParser.UnlockTablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#unlockTables.
    def exitUnlockTables(self, ctx:frameQLParser.UnlockTablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#setAutocommitStatement.
    def enterSetAutocommitStatement(self, ctx:frameQLParser.SetAutocommitStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#setAutocommitStatement.
    def exitSetAutocommitStatement(self, ctx:frameQLParser.SetAutocommitStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#setTransactionStatement.
    def enterSetTransactionStatement(self, ctx:frameQLParser.SetTransactionStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#setTransactionStatement.
    def exitSetTransactionStatement(self, ctx:frameQLParser.SetTransactionStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#transactionMode.
    def enterTransactionMode(self, ctx:frameQLParser.TransactionModeContext):
        pass

    # Exit a parse tree produced by frameQLParser#transactionMode.
    def exitTransactionMode(self, ctx:frameQLParser.TransactionModeContext):
        pass


    # Enter a parse tree produced by frameQLParser#lockTableElement.
    def enterLockTableElement(self, ctx:frameQLParser.LockTableElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#lockTableElement.
    def exitLockTableElement(self, ctx:frameQLParser.LockTableElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#lockAction.
    def enterLockAction(self, ctx:frameQLParser.LockActionContext):
        pass

    # Exit a parse tree produced by frameQLParser#lockAction.
    def exitLockAction(self, ctx:frameQLParser.LockActionContext):
        pass


    # Enter a parse tree produced by frameQLParser#transactionOption.
    def enterTransactionOption(self, ctx:frameQLParser.TransactionOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#transactionOption.
    def exitTransactionOption(self, ctx:frameQLParser.TransactionOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#transactionLevel.
    def enterTransactionLevel(self, ctx:frameQLParser.TransactionLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#transactionLevel.
    def exitTransactionLevel(self, ctx:frameQLParser.TransactionLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#changeMaster.
    def enterChangeMaster(self, ctx:frameQLParser.ChangeMasterContext):
        pass

    # Exit a parse tree produced by frameQLParser#changeMaster.
    def exitChangeMaster(self, ctx:frameQLParser.ChangeMasterContext):
        pass


    # Enter a parse tree produced by frameQLParser#changeReplicationFilter.
    def enterChangeReplicationFilter(self, ctx:frameQLParser.ChangeReplicationFilterContext):
        pass

    # Exit a parse tree produced by frameQLParser#changeReplicationFilter.
    def exitChangeReplicationFilter(self, ctx:frameQLParser.ChangeReplicationFilterContext):
        pass


    # Enter a parse tree produced by frameQLParser#purgeBinaryLogs.
    def enterPurgeBinaryLogs(self, ctx:frameQLParser.PurgeBinaryLogsContext):
        pass

    # Exit a parse tree produced by frameQLParser#purgeBinaryLogs.
    def exitPurgeBinaryLogs(self, ctx:frameQLParser.PurgeBinaryLogsContext):
        pass


    # Enter a parse tree produced by frameQLParser#resetMaster.
    def enterResetMaster(self, ctx:frameQLParser.ResetMasterContext):
        pass

    # Exit a parse tree produced by frameQLParser#resetMaster.
    def exitResetMaster(self, ctx:frameQLParser.ResetMasterContext):
        pass


    # Enter a parse tree produced by frameQLParser#resetSlave.
    def enterResetSlave(self, ctx:frameQLParser.ResetSlaveContext):
        pass

    # Exit a parse tree produced by frameQLParser#resetSlave.
    def exitResetSlave(self, ctx:frameQLParser.ResetSlaveContext):
        pass


    # Enter a parse tree produced by frameQLParser#startSlave.
    def enterStartSlave(self, ctx:frameQLParser.StartSlaveContext):
        pass

    # Exit a parse tree produced by frameQLParser#startSlave.
    def exitStartSlave(self, ctx:frameQLParser.StartSlaveContext):
        pass


    # Enter a parse tree produced by frameQLParser#stopSlave.
    def enterStopSlave(self, ctx:frameQLParser.StopSlaveContext):
        pass

    # Exit a parse tree produced by frameQLParser#stopSlave.
    def exitStopSlave(self, ctx:frameQLParser.StopSlaveContext):
        pass


    # Enter a parse tree produced by frameQLParser#startGroupReplication.
    def enterStartGroupReplication(self, ctx:frameQLParser.StartGroupReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#startGroupReplication.
    def exitStartGroupReplication(self, ctx:frameQLParser.StartGroupReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#stopGroupReplication.
    def enterStopGroupReplication(self, ctx:frameQLParser.StopGroupReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#stopGroupReplication.
    def exitStopGroupReplication(self, ctx:frameQLParser.StopGroupReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterStringOption.
    def enterMasterStringOption(self, ctx:frameQLParser.MasterStringOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterStringOption.
    def exitMasterStringOption(self, ctx:frameQLParser.MasterStringOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterDecimalOption.
    def enterMasterDecimalOption(self, ctx:frameQLParser.MasterDecimalOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterDecimalOption.
    def exitMasterDecimalOption(self, ctx:frameQLParser.MasterDecimalOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterBoolOption.
    def enterMasterBoolOption(self, ctx:frameQLParser.MasterBoolOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterBoolOption.
    def exitMasterBoolOption(self, ctx:frameQLParser.MasterBoolOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterRealOption.
    def enterMasterRealOption(self, ctx:frameQLParser.MasterRealOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterRealOption.
    def exitMasterRealOption(self, ctx:frameQLParser.MasterRealOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterUidListOption.
    def enterMasterUidListOption(self, ctx:frameQLParser.MasterUidListOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterUidListOption.
    def exitMasterUidListOption(self, ctx:frameQLParser.MasterUidListOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#stringMasterOption.
    def enterStringMasterOption(self, ctx:frameQLParser.StringMasterOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#stringMasterOption.
    def exitStringMasterOption(self, ctx:frameQLParser.StringMasterOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#decimalMasterOption.
    def enterDecimalMasterOption(self, ctx:frameQLParser.DecimalMasterOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#decimalMasterOption.
    def exitDecimalMasterOption(self, ctx:frameQLParser.DecimalMasterOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#boolMasterOption.
    def enterBoolMasterOption(self, ctx:frameQLParser.BoolMasterOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#boolMasterOption.
    def exitBoolMasterOption(self, ctx:frameQLParser.BoolMasterOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#channelOption.
    def enterChannelOption(self, ctx:frameQLParser.ChannelOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#channelOption.
    def exitChannelOption(self, ctx:frameQLParser.ChannelOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#doDbReplication.
    def enterDoDbReplication(self, ctx:frameQLParser.DoDbReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#doDbReplication.
    def exitDoDbReplication(self, ctx:frameQLParser.DoDbReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#ignoreDbReplication.
    def enterIgnoreDbReplication(self, ctx:frameQLParser.IgnoreDbReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#ignoreDbReplication.
    def exitIgnoreDbReplication(self, ctx:frameQLParser.IgnoreDbReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#doTableReplication.
    def enterDoTableReplication(self, ctx:frameQLParser.DoTableReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#doTableReplication.
    def exitDoTableReplication(self, ctx:frameQLParser.DoTableReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#ignoreTableReplication.
    def enterIgnoreTableReplication(self, ctx:frameQLParser.IgnoreTableReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#ignoreTableReplication.
    def exitIgnoreTableReplication(self, ctx:frameQLParser.IgnoreTableReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#wildDoTableReplication.
    def enterWildDoTableReplication(self, ctx:frameQLParser.WildDoTableReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#wildDoTableReplication.
    def exitWildDoTableReplication(self, ctx:frameQLParser.WildDoTableReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#wildIgnoreTableReplication.
    def enterWildIgnoreTableReplication(self, ctx:frameQLParser.WildIgnoreTableReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#wildIgnoreTableReplication.
    def exitWildIgnoreTableReplication(self, ctx:frameQLParser.WildIgnoreTableReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#rewriteDbReplication.
    def enterRewriteDbReplication(self, ctx:frameQLParser.RewriteDbReplicationContext):
        pass

    # Exit a parse tree produced by frameQLParser#rewriteDbReplication.
    def exitRewriteDbReplication(self, ctx:frameQLParser.RewriteDbReplicationContext):
        pass


    # Enter a parse tree produced by frameQLParser#tablePair.
    def enterTablePair(self, ctx:frameQLParser.TablePairContext):
        pass

    # Exit a parse tree produced by frameQLParser#tablePair.
    def exitTablePair(self, ctx:frameQLParser.TablePairContext):
        pass


    # Enter a parse tree produced by frameQLParser#threadType.
    def enterThreadType(self, ctx:frameQLParser.ThreadTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#threadType.
    def exitThreadType(self, ctx:frameQLParser.ThreadTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#gtidsUntilOption.
    def enterGtidsUntilOption(self, ctx:frameQLParser.GtidsUntilOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#gtidsUntilOption.
    def exitGtidsUntilOption(self, ctx:frameQLParser.GtidsUntilOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#masterLogUntilOption.
    def enterMasterLogUntilOption(self, ctx:frameQLParser.MasterLogUntilOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#masterLogUntilOption.
    def exitMasterLogUntilOption(self, ctx:frameQLParser.MasterLogUntilOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#relayLogUntilOption.
    def enterRelayLogUntilOption(self, ctx:frameQLParser.RelayLogUntilOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#relayLogUntilOption.
    def exitRelayLogUntilOption(self, ctx:frameQLParser.RelayLogUntilOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#sqlGapsUntilOption.
    def enterSqlGapsUntilOption(self, ctx:frameQLParser.SqlGapsUntilOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#sqlGapsUntilOption.
    def exitSqlGapsUntilOption(self, ctx:frameQLParser.SqlGapsUntilOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#userConnectionOption.
    def enterUserConnectionOption(self, ctx:frameQLParser.UserConnectionOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#userConnectionOption.
    def exitUserConnectionOption(self, ctx:frameQLParser.UserConnectionOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#passwordConnectionOption.
    def enterPasswordConnectionOption(self, ctx:frameQLParser.PasswordConnectionOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#passwordConnectionOption.
    def exitPasswordConnectionOption(self, ctx:frameQLParser.PasswordConnectionOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#defaultAuthConnectionOption.
    def enterDefaultAuthConnectionOption(self, ctx:frameQLParser.DefaultAuthConnectionOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#defaultAuthConnectionOption.
    def exitDefaultAuthConnectionOption(self, ctx:frameQLParser.DefaultAuthConnectionOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#pluginDirConnectionOption.
    def enterPluginDirConnectionOption(self, ctx:frameQLParser.PluginDirConnectionOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#pluginDirConnectionOption.
    def exitPluginDirConnectionOption(self, ctx:frameQLParser.PluginDirConnectionOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#gtuidSet.
    def enterGtuidSet(self, ctx:frameQLParser.GtuidSetContext):
        pass

    # Exit a parse tree produced by frameQLParser#gtuidSet.
    def exitGtuidSet(self, ctx:frameQLParser.GtuidSetContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaStartTransaction.
    def enterXaStartTransaction(self, ctx:frameQLParser.XaStartTransactionContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaStartTransaction.
    def exitXaStartTransaction(self, ctx:frameQLParser.XaStartTransactionContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaEndTransaction.
    def enterXaEndTransaction(self, ctx:frameQLParser.XaEndTransactionContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaEndTransaction.
    def exitXaEndTransaction(self, ctx:frameQLParser.XaEndTransactionContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaPrepareStatement.
    def enterXaPrepareStatement(self, ctx:frameQLParser.XaPrepareStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaPrepareStatement.
    def exitXaPrepareStatement(self, ctx:frameQLParser.XaPrepareStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaCommitWork.
    def enterXaCommitWork(self, ctx:frameQLParser.XaCommitWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaCommitWork.
    def exitXaCommitWork(self, ctx:frameQLParser.XaCommitWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaRollbackWork.
    def enterXaRollbackWork(self, ctx:frameQLParser.XaRollbackWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaRollbackWork.
    def exitXaRollbackWork(self, ctx:frameQLParser.XaRollbackWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#xaRecoverWork.
    def enterXaRecoverWork(self, ctx:frameQLParser.XaRecoverWorkContext):
        pass

    # Exit a parse tree produced by frameQLParser#xaRecoverWork.
    def exitXaRecoverWork(self, ctx:frameQLParser.XaRecoverWorkContext):
        pass


    # Enter a parse tree produced by frameQLParser#prepareStatement.
    def enterPrepareStatement(self, ctx:frameQLParser.PrepareStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#prepareStatement.
    def exitPrepareStatement(self, ctx:frameQLParser.PrepareStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#executeStatement.
    def enterExecuteStatement(self, ctx:frameQLParser.ExecuteStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#executeStatement.
    def exitExecuteStatement(self, ctx:frameQLParser.ExecuteStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#deallocatePrepare.
    def enterDeallocatePrepare(self, ctx:frameQLParser.DeallocatePrepareContext):
        pass

    # Exit a parse tree produced by frameQLParser#deallocatePrepare.
    def exitDeallocatePrepare(self, ctx:frameQLParser.DeallocatePrepareContext):
        pass


    # Enter a parse tree produced by frameQLParser#routineBody.
    def enterRoutineBody(self, ctx:frameQLParser.RoutineBodyContext):
        pass

    # Exit a parse tree produced by frameQLParser#routineBody.
    def exitRoutineBody(self, ctx:frameQLParser.RoutineBodyContext):
        pass


    # Enter a parse tree produced by frameQLParser#blockStatement.
    def enterBlockStatement(self, ctx:frameQLParser.BlockStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#blockStatement.
    def exitBlockStatement(self, ctx:frameQLParser.BlockStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#caseStatement.
    def enterCaseStatement(self, ctx:frameQLParser.CaseStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#caseStatement.
    def exitCaseStatement(self, ctx:frameQLParser.CaseStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#ifStatement.
    def enterIfStatement(self, ctx:frameQLParser.IfStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#ifStatement.
    def exitIfStatement(self, ctx:frameQLParser.IfStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#iterateStatement.
    def enterIterateStatement(self, ctx:frameQLParser.IterateStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#iterateStatement.
    def exitIterateStatement(self, ctx:frameQLParser.IterateStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#leaveStatement.
    def enterLeaveStatement(self, ctx:frameQLParser.LeaveStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#leaveStatement.
    def exitLeaveStatement(self, ctx:frameQLParser.LeaveStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#loopStatement.
    def enterLoopStatement(self, ctx:frameQLParser.LoopStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#loopStatement.
    def exitLoopStatement(self, ctx:frameQLParser.LoopStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#repeatStatement.
    def enterRepeatStatement(self, ctx:frameQLParser.RepeatStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#repeatStatement.
    def exitRepeatStatement(self, ctx:frameQLParser.RepeatStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#returnStatement.
    def enterReturnStatement(self, ctx:frameQLParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#returnStatement.
    def exitReturnStatement(self, ctx:frameQLParser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#whileStatement.
    def enterWhileStatement(self, ctx:frameQLParser.WhileStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#whileStatement.
    def exitWhileStatement(self, ctx:frameQLParser.WhileStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#CloseCursor.
    def enterCloseCursor(self, ctx:frameQLParser.CloseCursorContext):
        pass

    # Exit a parse tree produced by frameQLParser#CloseCursor.
    def exitCloseCursor(self, ctx:frameQLParser.CloseCursorContext):
        pass


    # Enter a parse tree produced by frameQLParser#FetchCursor.
    def enterFetchCursor(self, ctx:frameQLParser.FetchCursorContext):
        pass

    # Exit a parse tree produced by frameQLParser#FetchCursor.
    def exitFetchCursor(self, ctx:frameQLParser.FetchCursorContext):
        pass


    # Enter a parse tree produced by frameQLParser#OpenCursor.
    def enterOpenCursor(self, ctx:frameQLParser.OpenCursorContext):
        pass

    # Exit a parse tree produced by frameQLParser#OpenCursor.
    def exitOpenCursor(self, ctx:frameQLParser.OpenCursorContext):
        pass


    # Enter a parse tree produced by frameQLParser#declareVariable.
    def enterDeclareVariable(self, ctx:frameQLParser.DeclareVariableContext):
        pass

    # Exit a parse tree produced by frameQLParser#declareVariable.
    def exitDeclareVariable(self, ctx:frameQLParser.DeclareVariableContext):
        pass


    # Enter a parse tree produced by frameQLParser#declareCondition.
    def enterDeclareCondition(self, ctx:frameQLParser.DeclareConditionContext):
        pass

    # Exit a parse tree produced by frameQLParser#declareCondition.
    def exitDeclareCondition(self, ctx:frameQLParser.DeclareConditionContext):
        pass


    # Enter a parse tree produced by frameQLParser#declareCursor.
    def enterDeclareCursor(self, ctx:frameQLParser.DeclareCursorContext):
        pass

    # Exit a parse tree produced by frameQLParser#declareCursor.
    def exitDeclareCursor(self, ctx:frameQLParser.DeclareCursorContext):
        pass


    # Enter a parse tree produced by frameQLParser#declareHandler.
    def enterDeclareHandler(self, ctx:frameQLParser.DeclareHandlerContext):
        pass

    # Exit a parse tree produced by frameQLParser#declareHandler.
    def exitDeclareHandler(self, ctx:frameQLParser.DeclareHandlerContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionCode.
    def enterHandlerConditionCode(self, ctx:frameQLParser.HandlerConditionCodeContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionCode.
    def exitHandlerConditionCode(self, ctx:frameQLParser.HandlerConditionCodeContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionState.
    def enterHandlerConditionState(self, ctx:frameQLParser.HandlerConditionStateContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionState.
    def exitHandlerConditionState(self, ctx:frameQLParser.HandlerConditionStateContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionName.
    def enterHandlerConditionName(self, ctx:frameQLParser.HandlerConditionNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionName.
    def exitHandlerConditionName(self, ctx:frameQLParser.HandlerConditionNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionWarning.
    def enterHandlerConditionWarning(self, ctx:frameQLParser.HandlerConditionWarningContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionWarning.
    def exitHandlerConditionWarning(self, ctx:frameQLParser.HandlerConditionWarningContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionNotfound.
    def enterHandlerConditionNotfound(self, ctx:frameQLParser.HandlerConditionNotfoundContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionNotfound.
    def exitHandlerConditionNotfound(self, ctx:frameQLParser.HandlerConditionNotfoundContext):
        pass


    # Enter a parse tree produced by frameQLParser#handlerConditionException.
    def enterHandlerConditionException(self, ctx:frameQLParser.HandlerConditionExceptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#handlerConditionException.
    def exitHandlerConditionException(self, ctx:frameQLParser.HandlerConditionExceptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#procedureSqlStatement.
    def enterProcedureSqlStatement(self, ctx:frameQLParser.ProcedureSqlStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#procedureSqlStatement.
    def exitProcedureSqlStatement(self, ctx:frameQLParser.ProcedureSqlStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#caseAlternative.
    def enterCaseAlternative(self, ctx:frameQLParser.CaseAlternativeContext):
        pass

    # Exit a parse tree produced by frameQLParser#caseAlternative.
    def exitCaseAlternative(self, ctx:frameQLParser.CaseAlternativeContext):
        pass


    # Enter a parse tree produced by frameQLParser#elifAlternative.
    def enterElifAlternative(self, ctx:frameQLParser.ElifAlternativeContext):
        pass

    # Exit a parse tree produced by frameQLParser#elifAlternative.
    def exitElifAlternative(self, ctx:frameQLParser.ElifAlternativeContext):
        pass


    # Enter a parse tree produced by frameQLParser#alterUserMysqlV56.
    def enterAlterUserMysqlV56(self, ctx:frameQLParser.AlterUserMysqlV56Context):
        pass

    # Exit a parse tree produced by frameQLParser#alterUserMysqlV56.
    def exitAlterUserMysqlV56(self, ctx:frameQLParser.AlterUserMysqlV56Context):
        pass


    # Enter a parse tree produced by frameQLParser#alterUserMysqlV57.
    def enterAlterUserMysqlV57(self, ctx:frameQLParser.AlterUserMysqlV57Context):
        pass

    # Exit a parse tree produced by frameQLParser#alterUserMysqlV57.
    def exitAlterUserMysqlV57(self, ctx:frameQLParser.AlterUserMysqlV57Context):
        pass


    # Enter a parse tree produced by frameQLParser#createUserMysqlV56.
    def enterCreateUserMysqlV56(self, ctx:frameQLParser.CreateUserMysqlV56Context):
        pass

    # Exit a parse tree produced by frameQLParser#createUserMysqlV56.
    def exitCreateUserMysqlV56(self, ctx:frameQLParser.CreateUserMysqlV56Context):
        pass


    # Enter a parse tree produced by frameQLParser#createUserMysqlV57.
    def enterCreateUserMysqlV57(self, ctx:frameQLParser.CreateUserMysqlV57Context):
        pass

    # Exit a parse tree produced by frameQLParser#createUserMysqlV57.
    def exitCreateUserMysqlV57(self, ctx:frameQLParser.CreateUserMysqlV57Context):
        pass


    # Enter a parse tree produced by frameQLParser#dropUser.
    def enterDropUser(self, ctx:frameQLParser.DropUserContext):
        pass

    # Exit a parse tree produced by frameQLParser#dropUser.
    def exitDropUser(self, ctx:frameQLParser.DropUserContext):
        pass


    # Enter a parse tree produced by frameQLParser#grantStatement.
    def enterGrantStatement(self, ctx:frameQLParser.GrantStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#grantStatement.
    def exitGrantStatement(self, ctx:frameQLParser.GrantStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#grantProxy.
    def enterGrantProxy(self, ctx:frameQLParser.GrantProxyContext):
        pass

    # Exit a parse tree produced by frameQLParser#grantProxy.
    def exitGrantProxy(self, ctx:frameQLParser.GrantProxyContext):
        pass


    # Enter a parse tree produced by frameQLParser#renameUser.
    def enterRenameUser(self, ctx:frameQLParser.RenameUserContext):
        pass

    # Exit a parse tree produced by frameQLParser#renameUser.
    def exitRenameUser(self, ctx:frameQLParser.RenameUserContext):
        pass


    # Enter a parse tree produced by frameQLParser#detailRevoke.
    def enterDetailRevoke(self, ctx:frameQLParser.DetailRevokeContext):
        pass

    # Exit a parse tree produced by frameQLParser#detailRevoke.
    def exitDetailRevoke(self, ctx:frameQLParser.DetailRevokeContext):
        pass


    # Enter a parse tree produced by frameQLParser#shortRevoke.
    def enterShortRevoke(self, ctx:frameQLParser.ShortRevokeContext):
        pass

    # Exit a parse tree produced by frameQLParser#shortRevoke.
    def exitShortRevoke(self, ctx:frameQLParser.ShortRevokeContext):
        pass


    # Enter a parse tree produced by frameQLParser#revokeProxy.
    def enterRevokeProxy(self, ctx:frameQLParser.RevokeProxyContext):
        pass

    # Exit a parse tree produced by frameQLParser#revokeProxy.
    def exitRevokeProxy(self, ctx:frameQLParser.RevokeProxyContext):
        pass


    # Enter a parse tree produced by frameQLParser#setPasswordStatement.
    def enterSetPasswordStatement(self, ctx:frameQLParser.SetPasswordStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#setPasswordStatement.
    def exitSetPasswordStatement(self, ctx:frameQLParser.SetPasswordStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#userSpecification.
    def enterUserSpecification(self, ctx:frameQLParser.UserSpecificationContext):
        pass

    # Exit a parse tree produced by frameQLParser#userSpecification.
    def exitUserSpecification(self, ctx:frameQLParser.UserSpecificationContext):
        pass


    # Enter a parse tree produced by frameQLParser#passwordAuthOption.
    def enterPasswordAuthOption(self, ctx:frameQLParser.PasswordAuthOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#passwordAuthOption.
    def exitPasswordAuthOption(self, ctx:frameQLParser.PasswordAuthOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#stringAuthOption.
    def enterStringAuthOption(self, ctx:frameQLParser.StringAuthOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#stringAuthOption.
    def exitStringAuthOption(self, ctx:frameQLParser.StringAuthOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#hashAuthOption.
    def enterHashAuthOption(self, ctx:frameQLParser.HashAuthOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#hashAuthOption.
    def exitHashAuthOption(self, ctx:frameQLParser.HashAuthOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleAuthOption.
    def enterSimpleAuthOption(self, ctx:frameQLParser.SimpleAuthOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleAuthOption.
    def exitSimpleAuthOption(self, ctx:frameQLParser.SimpleAuthOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tlsOption.
    def enterTlsOption(self, ctx:frameQLParser.TlsOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tlsOption.
    def exitTlsOption(self, ctx:frameQLParser.TlsOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#userResourceOption.
    def enterUserResourceOption(self, ctx:frameQLParser.UserResourceOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#userResourceOption.
    def exitUserResourceOption(self, ctx:frameQLParser.UserResourceOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#userPasswordOption.
    def enterUserPasswordOption(self, ctx:frameQLParser.UserPasswordOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#userPasswordOption.
    def exitUserPasswordOption(self, ctx:frameQLParser.UserPasswordOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#userLockOption.
    def enterUserLockOption(self, ctx:frameQLParser.UserLockOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#userLockOption.
    def exitUserLockOption(self, ctx:frameQLParser.UserLockOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#privelegeClause.
    def enterPrivelegeClause(self, ctx:frameQLParser.PrivelegeClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#privelegeClause.
    def exitPrivelegeClause(self, ctx:frameQLParser.PrivelegeClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#privilege.
    def enterPrivilege(self, ctx:frameQLParser.PrivilegeContext):
        pass

    # Exit a parse tree produced by frameQLParser#privilege.
    def exitPrivilege(self, ctx:frameQLParser.PrivilegeContext):
        pass


    # Enter a parse tree produced by frameQLParser#currentSchemaPriviLevel.
    def enterCurrentSchemaPriviLevel(self, ctx:frameQLParser.CurrentSchemaPriviLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#currentSchemaPriviLevel.
    def exitCurrentSchemaPriviLevel(self, ctx:frameQLParser.CurrentSchemaPriviLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#globalPrivLevel.
    def enterGlobalPrivLevel(self, ctx:frameQLParser.GlobalPrivLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#globalPrivLevel.
    def exitGlobalPrivLevel(self, ctx:frameQLParser.GlobalPrivLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#definiteSchemaPrivLevel.
    def enterDefiniteSchemaPrivLevel(self, ctx:frameQLParser.DefiniteSchemaPrivLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#definiteSchemaPrivLevel.
    def exitDefiniteSchemaPrivLevel(self, ctx:frameQLParser.DefiniteSchemaPrivLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#definiteFullTablePrivLevel.
    def enterDefiniteFullTablePrivLevel(self, ctx:frameQLParser.DefiniteFullTablePrivLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#definiteFullTablePrivLevel.
    def exitDefiniteFullTablePrivLevel(self, ctx:frameQLParser.DefiniteFullTablePrivLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#definiteTablePrivLevel.
    def enterDefiniteTablePrivLevel(self, ctx:frameQLParser.DefiniteTablePrivLevelContext):
        pass

    # Exit a parse tree produced by frameQLParser#definiteTablePrivLevel.
    def exitDefiniteTablePrivLevel(self, ctx:frameQLParser.DefiniteTablePrivLevelContext):
        pass


    # Enter a parse tree produced by frameQLParser#renameUserClause.
    def enterRenameUserClause(self, ctx:frameQLParser.RenameUserClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#renameUserClause.
    def exitRenameUserClause(self, ctx:frameQLParser.RenameUserClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#analyzeTable.
    def enterAnalyzeTable(self, ctx:frameQLParser.AnalyzeTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#analyzeTable.
    def exitAnalyzeTable(self, ctx:frameQLParser.AnalyzeTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#checkTable.
    def enterCheckTable(self, ctx:frameQLParser.CheckTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#checkTable.
    def exitCheckTable(self, ctx:frameQLParser.CheckTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#checksumTable.
    def enterChecksumTable(self, ctx:frameQLParser.ChecksumTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#checksumTable.
    def exitChecksumTable(self, ctx:frameQLParser.ChecksumTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#optimizeTable.
    def enterOptimizeTable(self, ctx:frameQLParser.OptimizeTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#optimizeTable.
    def exitOptimizeTable(self, ctx:frameQLParser.OptimizeTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#repairTable.
    def enterRepairTable(self, ctx:frameQLParser.RepairTableContext):
        pass

    # Exit a parse tree produced by frameQLParser#repairTable.
    def exitRepairTable(self, ctx:frameQLParser.RepairTableContext):
        pass


    # Enter a parse tree produced by frameQLParser#checkTableOption.
    def enterCheckTableOption(self, ctx:frameQLParser.CheckTableOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#checkTableOption.
    def exitCheckTableOption(self, ctx:frameQLParser.CheckTableOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#createUdfunction.
    def enterCreateUdfunction(self, ctx:frameQLParser.CreateUdfunctionContext):
        pass

    # Exit a parse tree produced by frameQLParser#createUdfunction.
    def exitCreateUdfunction(self, ctx:frameQLParser.CreateUdfunctionContext):
        pass


    # Enter a parse tree produced by frameQLParser#installPlugin.
    def enterInstallPlugin(self, ctx:frameQLParser.InstallPluginContext):
        pass

    # Exit a parse tree produced by frameQLParser#installPlugin.
    def exitInstallPlugin(self, ctx:frameQLParser.InstallPluginContext):
        pass


    # Enter a parse tree produced by frameQLParser#uninstallPlugin.
    def enterUninstallPlugin(self, ctx:frameQLParser.UninstallPluginContext):
        pass

    # Exit a parse tree produced by frameQLParser#uninstallPlugin.
    def exitUninstallPlugin(self, ctx:frameQLParser.UninstallPluginContext):
        pass


    # Enter a parse tree produced by frameQLParser#setVariable.
    def enterSetVariable(self, ctx:frameQLParser.SetVariableContext):
        pass

    # Exit a parse tree produced by frameQLParser#setVariable.
    def exitSetVariable(self, ctx:frameQLParser.SetVariableContext):
        pass


    # Enter a parse tree produced by frameQLParser#setCharset.
    def enterSetCharset(self, ctx:frameQLParser.SetCharsetContext):
        pass

    # Exit a parse tree produced by frameQLParser#setCharset.
    def exitSetCharset(self, ctx:frameQLParser.SetCharsetContext):
        pass


    # Enter a parse tree produced by frameQLParser#setNames.
    def enterSetNames(self, ctx:frameQLParser.SetNamesContext):
        pass

    # Exit a parse tree produced by frameQLParser#setNames.
    def exitSetNames(self, ctx:frameQLParser.SetNamesContext):
        pass


    # Enter a parse tree produced by frameQLParser#setPassword.
    def enterSetPassword(self, ctx:frameQLParser.SetPasswordContext):
        pass

    # Exit a parse tree produced by frameQLParser#setPassword.
    def exitSetPassword(self, ctx:frameQLParser.SetPasswordContext):
        pass


    # Enter a parse tree produced by frameQLParser#setTransaction.
    def enterSetTransaction(self, ctx:frameQLParser.SetTransactionContext):
        pass

    # Exit a parse tree produced by frameQLParser#setTransaction.
    def exitSetTransaction(self, ctx:frameQLParser.SetTransactionContext):
        pass


    # Enter a parse tree produced by frameQLParser#setAutocommit.
    def enterSetAutocommit(self, ctx:frameQLParser.SetAutocommitContext):
        pass

    # Exit a parse tree produced by frameQLParser#setAutocommit.
    def exitSetAutocommit(self, ctx:frameQLParser.SetAutocommitContext):
        pass


    # Enter a parse tree produced by frameQLParser#showMasterLogs.
    def enterShowMasterLogs(self, ctx:frameQLParser.ShowMasterLogsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showMasterLogs.
    def exitShowMasterLogs(self, ctx:frameQLParser.ShowMasterLogsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showLogEvents.
    def enterShowLogEvents(self, ctx:frameQLParser.ShowLogEventsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showLogEvents.
    def exitShowLogEvents(self, ctx:frameQLParser.ShowLogEventsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showObjectFilter.
    def enterShowObjectFilter(self, ctx:frameQLParser.ShowObjectFilterContext):
        pass

    # Exit a parse tree produced by frameQLParser#showObjectFilter.
    def exitShowObjectFilter(self, ctx:frameQLParser.ShowObjectFilterContext):
        pass


    # Enter a parse tree produced by frameQLParser#showColumns.
    def enterShowColumns(self, ctx:frameQLParser.ShowColumnsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showColumns.
    def exitShowColumns(self, ctx:frameQLParser.ShowColumnsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showCreateDb.
    def enterShowCreateDb(self, ctx:frameQLParser.ShowCreateDbContext):
        pass

    # Exit a parse tree produced by frameQLParser#showCreateDb.
    def exitShowCreateDb(self, ctx:frameQLParser.ShowCreateDbContext):
        pass


    # Enter a parse tree produced by frameQLParser#showCreateFullIdObject.
    def enterShowCreateFullIdObject(self, ctx:frameQLParser.ShowCreateFullIdObjectContext):
        pass

    # Exit a parse tree produced by frameQLParser#showCreateFullIdObject.
    def exitShowCreateFullIdObject(self, ctx:frameQLParser.ShowCreateFullIdObjectContext):
        pass


    # Enter a parse tree produced by frameQLParser#showCreateUser.
    def enterShowCreateUser(self, ctx:frameQLParser.ShowCreateUserContext):
        pass

    # Exit a parse tree produced by frameQLParser#showCreateUser.
    def exitShowCreateUser(self, ctx:frameQLParser.ShowCreateUserContext):
        pass


    # Enter a parse tree produced by frameQLParser#showEngine.
    def enterShowEngine(self, ctx:frameQLParser.ShowEngineContext):
        pass

    # Exit a parse tree produced by frameQLParser#showEngine.
    def exitShowEngine(self, ctx:frameQLParser.ShowEngineContext):
        pass


    # Enter a parse tree produced by frameQLParser#showGlobalInfo.
    def enterShowGlobalInfo(self, ctx:frameQLParser.ShowGlobalInfoContext):
        pass

    # Exit a parse tree produced by frameQLParser#showGlobalInfo.
    def exitShowGlobalInfo(self, ctx:frameQLParser.ShowGlobalInfoContext):
        pass


    # Enter a parse tree produced by frameQLParser#showErrors.
    def enterShowErrors(self, ctx:frameQLParser.ShowErrorsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showErrors.
    def exitShowErrors(self, ctx:frameQLParser.ShowErrorsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showCountErrors.
    def enterShowCountErrors(self, ctx:frameQLParser.ShowCountErrorsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showCountErrors.
    def exitShowCountErrors(self, ctx:frameQLParser.ShowCountErrorsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showSchemaFilter.
    def enterShowSchemaFilter(self, ctx:frameQLParser.ShowSchemaFilterContext):
        pass

    # Exit a parse tree produced by frameQLParser#showSchemaFilter.
    def exitShowSchemaFilter(self, ctx:frameQLParser.ShowSchemaFilterContext):
        pass


    # Enter a parse tree produced by frameQLParser#showRoutine.
    def enterShowRoutine(self, ctx:frameQLParser.ShowRoutineContext):
        pass

    # Exit a parse tree produced by frameQLParser#showRoutine.
    def exitShowRoutine(self, ctx:frameQLParser.ShowRoutineContext):
        pass


    # Enter a parse tree produced by frameQLParser#showGrants.
    def enterShowGrants(self, ctx:frameQLParser.ShowGrantsContext):
        pass

    # Exit a parse tree produced by frameQLParser#showGrants.
    def exitShowGrants(self, ctx:frameQLParser.ShowGrantsContext):
        pass


    # Enter a parse tree produced by frameQLParser#showIndexes.
    def enterShowIndexes(self, ctx:frameQLParser.ShowIndexesContext):
        pass

    # Exit a parse tree produced by frameQLParser#showIndexes.
    def exitShowIndexes(self, ctx:frameQLParser.ShowIndexesContext):
        pass


    # Enter a parse tree produced by frameQLParser#showOpenTables.
    def enterShowOpenTables(self, ctx:frameQLParser.ShowOpenTablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#showOpenTables.
    def exitShowOpenTables(self, ctx:frameQLParser.ShowOpenTablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#showProfile.
    def enterShowProfile(self, ctx:frameQLParser.ShowProfileContext):
        pass

    # Exit a parse tree produced by frameQLParser#showProfile.
    def exitShowProfile(self, ctx:frameQLParser.ShowProfileContext):
        pass


    # Enter a parse tree produced by frameQLParser#showSlaveStatus.
    def enterShowSlaveStatus(self, ctx:frameQLParser.ShowSlaveStatusContext):
        pass

    # Exit a parse tree produced by frameQLParser#showSlaveStatus.
    def exitShowSlaveStatus(self, ctx:frameQLParser.ShowSlaveStatusContext):
        pass


    # Enter a parse tree produced by frameQLParser#variableClause.
    def enterVariableClause(self, ctx:frameQLParser.VariableClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#variableClause.
    def exitVariableClause(self, ctx:frameQLParser.VariableClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#showCommonEntity.
    def enterShowCommonEntity(self, ctx:frameQLParser.ShowCommonEntityContext):
        pass

    # Exit a parse tree produced by frameQLParser#showCommonEntity.
    def exitShowCommonEntity(self, ctx:frameQLParser.ShowCommonEntityContext):
        pass


    # Enter a parse tree produced by frameQLParser#showFilter.
    def enterShowFilter(self, ctx:frameQLParser.ShowFilterContext):
        pass

    # Exit a parse tree produced by frameQLParser#showFilter.
    def exitShowFilter(self, ctx:frameQLParser.ShowFilterContext):
        pass


    # Enter a parse tree produced by frameQLParser#showGlobalInfoClause.
    def enterShowGlobalInfoClause(self, ctx:frameQLParser.ShowGlobalInfoClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#showGlobalInfoClause.
    def exitShowGlobalInfoClause(self, ctx:frameQLParser.ShowGlobalInfoClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#showSchemaEntity.
    def enterShowSchemaEntity(self, ctx:frameQLParser.ShowSchemaEntityContext):
        pass

    # Exit a parse tree produced by frameQLParser#showSchemaEntity.
    def exitShowSchemaEntity(self, ctx:frameQLParser.ShowSchemaEntityContext):
        pass


    # Enter a parse tree produced by frameQLParser#showProfileType.
    def enterShowProfileType(self, ctx:frameQLParser.ShowProfileTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#showProfileType.
    def exitShowProfileType(self, ctx:frameQLParser.ShowProfileTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#binlogStatement.
    def enterBinlogStatement(self, ctx:frameQLParser.BinlogStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#binlogStatement.
    def exitBinlogStatement(self, ctx:frameQLParser.BinlogStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#cacheIndexStatement.
    def enterCacheIndexStatement(self, ctx:frameQLParser.CacheIndexStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#cacheIndexStatement.
    def exitCacheIndexStatement(self, ctx:frameQLParser.CacheIndexStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#flushStatement.
    def enterFlushStatement(self, ctx:frameQLParser.FlushStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#flushStatement.
    def exitFlushStatement(self, ctx:frameQLParser.FlushStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#killStatement.
    def enterKillStatement(self, ctx:frameQLParser.KillStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#killStatement.
    def exitKillStatement(self, ctx:frameQLParser.KillStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#loadIndexIntoCache.
    def enterLoadIndexIntoCache(self, ctx:frameQLParser.LoadIndexIntoCacheContext):
        pass

    # Exit a parse tree produced by frameQLParser#loadIndexIntoCache.
    def exitLoadIndexIntoCache(self, ctx:frameQLParser.LoadIndexIntoCacheContext):
        pass


    # Enter a parse tree produced by frameQLParser#resetStatement.
    def enterResetStatement(self, ctx:frameQLParser.ResetStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#resetStatement.
    def exitResetStatement(self, ctx:frameQLParser.ResetStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#shutdownStatement.
    def enterShutdownStatement(self, ctx:frameQLParser.ShutdownStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#shutdownStatement.
    def exitShutdownStatement(self, ctx:frameQLParser.ShutdownStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableIndexes.
    def enterTableIndexes(self, ctx:frameQLParser.TableIndexesContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableIndexes.
    def exitTableIndexes(self, ctx:frameQLParser.TableIndexesContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleFlushOption.
    def enterSimpleFlushOption(self, ctx:frameQLParser.SimpleFlushOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleFlushOption.
    def exitSimpleFlushOption(self, ctx:frameQLParser.SimpleFlushOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#channelFlushOption.
    def enterChannelFlushOption(self, ctx:frameQLParser.ChannelFlushOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#channelFlushOption.
    def exitChannelFlushOption(self, ctx:frameQLParser.ChannelFlushOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableFlushOption.
    def enterTableFlushOption(self, ctx:frameQLParser.TableFlushOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableFlushOption.
    def exitTableFlushOption(self, ctx:frameQLParser.TableFlushOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#flushTableOption.
    def enterFlushTableOption(self, ctx:frameQLParser.FlushTableOptionContext):
        pass

    # Exit a parse tree produced by frameQLParser#flushTableOption.
    def exitFlushTableOption(self, ctx:frameQLParser.FlushTableOptionContext):
        pass


    # Enter a parse tree produced by frameQLParser#loadedTableIndexes.
    def enterLoadedTableIndexes(self, ctx:frameQLParser.LoadedTableIndexesContext):
        pass

    # Exit a parse tree produced by frameQLParser#loadedTableIndexes.
    def exitLoadedTableIndexes(self, ctx:frameQLParser.LoadedTableIndexesContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleDescribeStatement.
    def enterSimpleDescribeStatement(self, ctx:frameQLParser.SimpleDescribeStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleDescribeStatement.
    def exitSimpleDescribeStatement(self, ctx:frameQLParser.SimpleDescribeStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#fullDescribeStatement.
    def enterFullDescribeStatement(self, ctx:frameQLParser.FullDescribeStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#fullDescribeStatement.
    def exitFullDescribeStatement(self, ctx:frameQLParser.FullDescribeStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#helpStatement.
    def enterHelpStatement(self, ctx:frameQLParser.HelpStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#helpStatement.
    def exitHelpStatement(self, ctx:frameQLParser.HelpStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#useStatement.
    def enterUseStatement(self, ctx:frameQLParser.UseStatementContext):
        pass

    # Exit a parse tree produced by frameQLParser#useStatement.
    def exitUseStatement(self, ctx:frameQLParser.UseStatementContext):
        pass


    # Enter a parse tree produced by frameQLParser#describeStatements.
    def enterDescribeStatements(self, ctx:frameQLParser.DescribeStatementsContext):
        pass

    # Exit a parse tree produced by frameQLParser#describeStatements.
    def exitDescribeStatements(self, ctx:frameQLParser.DescribeStatementsContext):
        pass


    # Enter a parse tree produced by frameQLParser#describeConnection.
    def enterDescribeConnection(self, ctx:frameQLParser.DescribeConnectionContext):
        pass

    # Exit a parse tree produced by frameQLParser#describeConnection.
    def exitDescribeConnection(self, ctx:frameQLParser.DescribeConnectionContext):
        pass


    # Enter a parse tree produced by frameQLParser#fullId.
    def enterFullId(self, ctx:frameQLParser.FullIdContext):
        pass

    # Exit a parse tree produced by frameQLParser#fullId.
    def exitFullId(self, ctx:frameQLParser.FullIdContext):
        pass


    # Enter a parse tree produced by frameQLParser#tableName.
    def enterTableName(self, ctx:frameQLParser.TableNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#tableName.
    def exitTableName(self, ctx:frameQLParser.TableNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#fullColumnName.
    def enterFullColumnName(self, ctx:frameQLParser.FullColumnNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#fullColumnName.
    def exitFullColumnName(self, ctx:frameQLParser.FullColumnNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexColumnName.
    def enterIndexColumnName(self, ctx:frameQLParser.IndexColumnNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexColumnName.
    def exitIndexColumnName(self, ctx:frameQLParser.IndexColumnNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#userName.
    def enterUserName(self, ctx:frameQLParser.UserNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#userName.
    def exitUserName(self, ctx:frameQLParser.UserNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#mysqlVariable.
    def enterMysqlVariable(self, ctx:frameQLParser.MysqlVariableContext):
        pass

    # Exit a parse tree produced by frameQLParser#mysqlVariable.
    def exitMysqlVariable(self, ctx:frameQLParser.MysqlVariableContext):
        pass


    # Enter a parse tree produced by frameQLParser#charsetName.
    def enterCharsetName(self, ctx:frameQLParser.CharsetNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#charsetName.
    def exitCharsetName(self, ctx:frameQLParser.CharsetNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#collationName.
    def enterCollationName(self, ctx:frameQLParser.CollationNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#collationName.
    def exitCollationName(self, ctx:frameQLParser.CollationNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#engineName.
    def enterEngineName(self, ctx:frameQLParser.EngineNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#engineName.
    def exitEngineName(self, ctx:frameQLParser.EngineNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#uuidSet.
    def enterUuidSet(self, ctx:frameQLParser.UuidSetContext):
        pass

    # Exit a parse tree produced by frameQLParser#uuidSet.
    def exitUuidSet(self, ctx:frameQLParser.UuidSetContext):
        pass


    # Enter a parse tree produced by frameQLParser#xid.
    def enterXid(self, ctx:frameQLParser.XidContext):
        pass

    # Exit a parse tree produced by frameQLParser#xid.
    def exitXid(self, ctx:frameQLParser.XidContext):
        pass


    # Enter a parse tree produced by frameQLParser#xuidStringId.
    def enterXuidStringId(self, ctx:frameQLParser.XuidStringIdContext):
        pass

    # Exit a parse tree produced by frameQLParser#xuidStringId.
    def exitXuidStringId(self, ctx:frameQLParser.XuidStringIdContext):
        pass


    # Enter a parse tree produced by frameQLParser#authPlugin.
    def enterAuthPlugin(self, ctx:frameQLParser.AuthPluginContext):
        pass

    # Exit a parse tree produced by frameQLParser#authPlugin.
    def exitAuthPlugin(self, ctx:frameQLParser.AuthPluginContext):
        pass


    # Enter a parse tree produced by frameQLParser#uid.
    def enterUid(self, ctx:frameQLParser.UidContext):
        pass

    # Exit a parse tree produced by frameQLParser#uid.
    def exitUid(self, ctx:frameQLParser.UidContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleId.
    def enterSimpleId(self, ctx:frameQLParser.SimpleIdContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleId.
    def exitSimpleId(self, ctx:frameQLParser.SimpleIdContext):
        pass


    # Enter a parse tree produced by frameQLParser#dottedId.
    def enterDottedId(self, ctx:frameQLParser.DottedIdContext):
        pass

    # Exit a parse tree produced by frameQLParser#dottedId.
    def exitDottedId(self, ctx:frameQLParser.DottedIdContext):
        pass


    # Enter a parse tree produced by frameQLParser#decimalLiteral.
    def enterDecimalLiteral(self, ctx:frameQLParser.DecimalLiteralContext):
        pass

    # Exit a parse tree produced by frameQLParser#decimalLiteral.
    def exitDecimalLiteral(self, ctx:frameQLParser.DecimalLiteralContext):
        pass


    # Enter a parse tree produced by frameQLParser#fileSizeLiteral.
    def enterFileSizeLiteral(self, ctx:frameQLParser.FileSizeLiteralContext):
        pass

    # Exit a parse tree produced by frameQLParser#fileSizeLiteral.
    def exitFileSizeLiteral(self, ctx:frameQLParser.FileSizeLiteralContext):
        pass


    # Enter a parse tree produced by frameQLParser#stringLiteral.
    def enterStringLiteral(self, ctx:frameQLParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by frameQLParser#stringLiteral.
    def exitStringLiteral(self, ctx:frameQLParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by frameQLParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:frameQLParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by frameQLParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:frameQLParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by frameQLParser#hexadecimalLiteral.
    def enterHexadecimalLiteral(self, ctx:frameQLParser.HexadecimalLiteralContext):
        pass

    # Exit a parse tree produced by frameQLParser#hexadecimalLiteral.
    def exitHexadecimalLiteral(self, ctx:frameQLParser.HexadecimalLiteralContext):
        pass


    # Enter a parse tree produced by frameQLParser#nullNotnull.
    def enterNullNotnull(self, ctx:frameQLParser.NullNotnullContext):
        pass

    # Exit a parse tree produced by frameQLParser#nullNotnull.
    def exitNullNotnull(self, ctx:frameQLParser.NullNotnullContext):
        pass


    # Enter a parse tree produced by frameQLParser#constant.
    def enterConstant(self, ctx:frameQLParser.ConstantContext):
        pass

    # Exit a parse tree produced by frameQLParser#constant.
    def exitConstant(self, ctx:frameQLParser.ConstantContext):
        pass


    # Enter a parse tree produced by frameQLParser#stringDataType.
    def enterStringDataType(self, ctx:frameQLParser.StringDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#stringDataType.
    def exitStringDataType(self, ctx:frameQLParser.StringDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#dimensionDataType.
    def enterDimensionDataType(self, ctx:frameQLParser.DimensionDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#dimensionDataType.
    def exitDimensionDataType(self, ctx:frameQLParser.DimensionDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleDataType.
    def enterSimpleDataType(self, ctx:frameQLParser.SimpleDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleDataType.
    def exitSimpleDataType(self, ctx:frameQLParser.SimpleDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#collectionDataType.
    def enterCollectionDataType(self, ctx:frameQLParser.CollectionDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#collectionDataType.
    def exitCollectionDataType(self, ctx:frameQLParser.CollectionDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#spatialDataType.
    def enterSpatialDataType(self, ctx:frameQLParser.SpatialDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#spatialDataType.
    def exitSpatialDataType(self, ctx:frameQLParser.SpatialDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#convertedDataType.
    def enterConvertedDataType(self, ctx:frameQLParser.ConvertedDataTypeContext):
        pass

    # Exit a parse tree produced by frameQLParser#convertedDataType.
    def exitConvertedDataType(self, ctx:frameQLParser.ConvertedDataTypeContext):
        pass


    # Enter a parse tree produced by frameQLParser#lengthOneDimension.
    def enterLengthOneDimension(self, ctx:frameQLParser.LengthOneDimensionContext):
        pass

    # Exit a parse tree produced by frameQLParser#lengthOneDimension.
    def exitLengthOneDimension(self, ctx:frameQLParser.LengthOneDimensionContext):
        pass


    # Enter a parse tree produced by frameQLParser#lengthTwoDimension.
    def enterLengthTwoDimension(self, ctx:frameQLParser.LengthTwoDimensionContext):
        pass

    # Exit a parse tree produced by frameQLParser#lengthTwoDimension.
    def exitLengthTwoDimension(self, ctx:frameQLParser.LengthTwoDimensionContext):
        pass


    # Enter a parse tree produced by frameQLParser#lengthTwoOptionalDimension.
    def enterLengthTwoOptionalDimension(self, ctx:frameQLParser.LengthTwoOptionalDimensionContext):
        pass

    # Exit a parse tree produced by frameQLParser#lengthTwoOptionalDimension.
    def exitLengthTwoOptionalDimension(self, ctx:frameQLParser.LengthTwoOptionalDimensionContext):
        pass


    # Enter a parse tree produced by frameQLParser#uidList.
    def enterUidList(self, ctx:frameQLParser.UidListContext):
        pass

    # Exit a parse tree produced by frameQLParser#uidList.
    def exitUidList(self, ctx:frameQLParser.UidListContext):
        pass


    # Enter a parse tree produced by frameQLParser#tables.
    def enterTables(self, ctx:frameQLParser.TablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#tables.
    def exitTables(self, ctx:frameQLParser.TablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#indexColumnNames.
    def enterIndexColumnNames(self, ctx:frameQLParser.IndexColumnNamesContext):
        pass

    # Exit a parse tree produced by frameQLParser#indexColumnNames.
    def exitIndexColumnNames(self, ctx:frameQLParser.IndexColumnNamesContext):
        pass


    # Enter a parse tree produced by frameQLParser#expressions.
    def enterExpressions(self, ctx:frameQLParser.ExpressionsContext):
        pass

    # Exit a parse tree produced by frameQLParser#expressions.
    def exitExpressions(self, ctx:frameQLParser.ExpressionsContext):
        pass


    # Enter a parse tree produced by frameQLParser#expressionsWithDefaults.
    def enterExpressionsWithDefaults(self, ctx:frameQLParser.ExpressionsWithDefaultsContext):
        pass

    # Exit a parse tree produced by frameQLParser#expressionsWithDefaults.
    def exitExpressionsWithDefaults(self, ctx:frameQLParser.ExpressionsWithDefaultsContext):
        pass


    # Enter a parse tree produced by frameQLParser#constants.
    def enterConstants(self, ctx:frameQLParser.ConstantsContext):
        pass

    # Exit a parse tree produced by frameQLParser#constants.
    def exitConstants(self, ctx:frameQLParser.ConstantsContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleStrings.
    def enterSimpleStrings(self, ctx:frameQLParser.SimpleStringsContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleStrings.
    def exitSimpleStrings(self, ctx:frameQLParser.SimpleStringsContext):
        pass


    # Enter a parse tree produced by frameQLParser#userVariables.
    def enterUserVariables(self, ctx:frameQLParser.UserVariablesContext):
        pass

    # Exit a parse tree produced by frameQLParser#userVariables.
    def exitUserVariables(self, ctx:frameQLParser.UserVariablesContext):
        pass


    # Enter a parse tree produced by frameQLParser#defaultValue.
    def enterDefaultValue(self, ctx:frameQLParser.DefaultValueContext):
        pass

    # Exit a parse tree produced by frameQLParser#defaultValue.
    def exitDefaultValue(self, ctx:frameQLParser.DefaultValueContext):
        pass


    # Enter a parse tree produced by frameQLParser#currentTimestamp.
    def enterCurrentTimestamp(self, ctx:frameQLParser.CurrentTimestampContext):
        pass

    # Exit a parse tree produced by frameQLParser#currentTimestamp.
    def exitCurrentTimestamp(self, ctx:frameQLParser.CurrentTimestampContext):
        pass


    # Enter a parse tree produced by frameQLParser#expressionOrDefault.
    def enterExpressionOrDefault(self, ctx:frameQLParser.ExpressionOrDefaultContext):
        pass

    # Exit a parse tree produced by frameQLParser#expressionOrDefault.
    def exitExpressionOrDefault(self, ctx:frameQLParser.ExpressionOrDefaultContext):
        pass


    # Enter a parse tree produced by frameQLParser#ifExists.
    def enterIfExists(self, ctx:frameQLParser.IfExistsContext):
        pass

    # Exit a parse tree produced by frameQLParser#ifExists.
    def exitIfExists(self, ctx:frameQLParser.IfExistsContext):
        pass


    # Enter a parse tree produced by frameQLParser#ifNotExists.
    def enterIfNotExists(self, ctx:frameQLParser.IfNotExistsContext):
        pass

    # Exit a parse tree produced by frameQLParser#ifNotExists.
    def exitIfNotExists(self, ctx:frameQLParser.IfNotExistsContext):
        pass


    # Enter a parse tree produced by frameQLParser#specificFunctionCall.
    def enterSpecificFunctionCall(self, ctx:frameQLParser.SpecificFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#specificFunctionCall.
    def exitSpecificFunctionCall(self, ctx:frameQLParser.SpecificFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#aggregateFunctionCall.
    def enterAggregateFunctionCall(self, ctx:frameQLParser.AggregateFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#aggregateFunctionCall.
    def exitAggregateFunctionCall(self, ctx:frameQLParser.AggregateFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#scalarFunctionCall.
    def enterScalarFunctionCall(self, ctx:frameQLParser.ScalarFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#scalarFunctionCall.
    def exitScalarFunctionCall(self, ctx:frameQLParser.ScalarFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#udfFunctionCall.
    def enterUdfFunctionCall(self, ctx:frameQLParser.UdfFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#udfFunctionCall.
    def exitUdfFunctionCall(self, ctx:frameQLParser.UdfFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#passwordFunctionCall.
    def enterPasswordFunctionCall(self, ctx:frameQLParser.PasswordFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#passwordFunctionCall.
    def exitPasswordFunctionCall(self, ctx:frameQLParser.PasswordFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#simpleFunctionCall.
    def enterSimpleFunctionCall(self, ctx:frameQLParser.SimpleFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#simpleFunctionCall.
    def exitSimpleFunctionCall(self, ctx:frameQLParser.SimpleFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#dataTypeFunctionCall.
    def enterDataTypeFunctionCall(self, ctx:frameQLParser.DataTypeFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#dataTypeFunctionCall.
    def exitDataTypeFunctionCall(self, ctx:frameQLParser.DataTypeFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#valuesFunctionCall.
    def enterValuesFunctionCall(self, ctx:frameQLParser.ValuesFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#valuesFunctionCall.
    def exitValuesFunctionCall(self, ctx:frameQLParser.ValuesFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#caseFunctionCall.
    def enterCaseFunctionCall(self, ctx:frameQLParser.CaseFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#caseFunctionCall.
    def exitCaseFunctionCall(self, ctx:frameQLParser.CaseFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#charFunctionCall.
    def enterCharFunctionCall(self, ctx:frameQLParser.CharFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#charFunctionCall.
    def exitCharFunctionCall(self, ctx:frameQLParser.CharFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#positionFunctionCall.
    def enterPositionFunctionCall(self, ctx:frameQLParser.PositionFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#positionFunctionCall.
    def exitPositionFunctionCall(self, ctx:frameQLParser.PositionFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#substrFunctionCall.
    def enterSubstrFunctionCall(self, ctx:frameQLParser.SubstrFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#substrFunctionCall.
    def exitSubstrFunctionCall(self, ctx:frameQLParser.SubstrFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#trimFunctionCall.
    def enterTrimFunctionCall(self, ctx:frameQLParser.TrimFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#trimFunctionCall.
    def exitTrimFunctionCall(self, ctx:frameQLParser.TrimFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#weightFunctionCall.
    def enterWeightFunctionCall(self, ctx:frameQLParser.WeightFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#weightFunctionCall.
    def exitWeightFunctionCall(self, ctx:frameQLParser.WeightFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#extractFunctionCall.
    def enterExtractFunctionCall(self, ctx:frameQLParser.ExtractFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#extractFunctionCall.
    def exitExtractFunctionCall(self, ctx:frameQLParser.ExtractFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#getFormatFunctionCall.
    def enterGetFormatFunctionCall(self, ctx:frameQLParser.GetFormatFunctionCallContext):
        pass

    # Exit a parse tree produced by frameQLParser#getFormatFunctionCall.
    def exitGetFormatFunctionCall(self, ctx:frameQLParser.GetFormatFunctionCallContext):
        pass


    # Enter a parse tree produced by frameQLParser#caseFuncAlternative.
    def enterCaseFuncAlternative(self, ctx:frameQLParser.CaseFuncAlternativeContext):
        pass

    # Exit a parse tree produced by frameQLParser#caseFuncAlternative.
    def exitCaseFuncAlternative(self, ctx:frameQLParser.CaseFuncAlternativeContext):
        pass


    # Enter a parse tree produced by frameQLParser#levelWeightList.
    def enterLevelWeightList(self, ctx:frameQLParser.LevelWeightListContext):
        pass

    # Exit a parse tree produced by frameQLParser#levelWeightList.
    def exitLevelWeightList(self, ctx:frameQLParser.LevelWeightListContext):
        pass


    # Enter a parse tree produced by frameQLParser#levelWeightRange.
    def enterLevelWeightRange(self, ctx:frameQLParser.LevelWeightRangeContext):
        pass

    # Exit a parse tree produced by frameQLParser#levelWeightRange.
    def exitLevelWeightRange(self, ctx:frameQLParser.LevelWeightRangeContext):
        pass


    # Enter a parse tree produced by frameQLParser#levelInWeightListElement.
    def enterLevelInWeightListElement(self, ctx:frameQLParser.LevelInWeightListElementContext):
        pass

    # Exit a parse tree produced by frameQLParser#levelInWeightListElement.
    def exitLevelInWeightListElement(self, ctx:frameQLParser.LevelInWeightListElementContext):
        pass


    # Enter a parse tree produced by frameQLParser#aggregateWindowedFunction.
    def enterAggregateWindowedFunction(self, ctx:frameQLParser.AggregateWindowedFunctionContext):
        pass

    # Exit a parse tree produced by frameQLParser#aggregateWindowedFunction.
    def exitAggregateWindowedFunction(self, ctx:frameQLParser.AggregateWindowedFunctionContext):
        pass


    # Enter a parse tree produced by frameQLParser#scalarFunctionName.
    def enterScalarFunctionName(self, ctx:frameQLParser.ScalarFunctionNameContext):
        pass

    # Exit a parse tree produced by frameQLParser#scalarFunctionName.
    def exitScalarFunctionName(self, ctx:frameQLParser.ScalarFunctionNameContext):
        pass


    # Enter a parse tree produced by frameQLParser#passwordFunctionClause.
    def enterPasswordFunctionClause(self, ctx:frameQLParser.PasswordFunctionClauseContext):
        pass

    # Exit a parse tree produced by frameQLParser#passwordFunctionClause.
    def exitPasswordFunctionClause(self, ctx:frameQLParser.PasswordFunctionClauseContext):
        pass


    # Enter a parse tree produced by frameQLParser#functionArgs.
    def enterFunctionArgs(self, ctx:frameQLParser.FunctionArgsContext):
        pass

    # Exit a parse tree produced by frameQLParser#functionArgs.
    def exitFunctionArgs(self, ctx:frameQLParser.FunctionArgsContext):
        pass


    # Enter a parse tree produced by frameQLParser#functionArg.
    def enterFunctionArg(self, ctx:frameQLParser.FunctionArgContext):
        pass

    # Exit a parse tree produced by frameQLParser#functionArg.
    def exitFunctionArg(self, ctx:frameQLParser.FunctionArgContext):
        pass


    # Enter a parse tree produced by frameQLParser#isExpression.
    def enterIsExpression(self, ctx:frameQLParser.IsExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#isExpression.
    def exitIsExpression(self, ctx:frameQLParser.IsExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#notExpression.
    def enterNotExpression(self, ctx:frameQLParser.NotExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#notExpression.
    def exitNotExpression(self, ctx:frameQLParser.NotExpressionContext):
        pass


    # Enter a parse tree produced by frameQLParser#logicalExpression.
    def enterLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#logicalExpression.
    # The operators are traversed in the correct order, so just add to the output list
    def exitLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        # if ctx.expression(0).getText()[0] == "(" and ctx.expression(1).getText()[0] == "(":
        #     self.bothInParentheses = True
        #     print("need different output format")
        #     print()
        self.output_operator.append(ctx.logicalOperator().getText())

    # Enter a parse tree produced by frameQLParser#predicateExpression.
    def enterPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        pass

    # Exit a parse tree produced by frameQLParser#predicateExpression.
    # The predicates are traversed from the bottom level up to the 2nd top level.
    # Whenever a predicate with parentheses are encountered, the two predicates before it are the predicates inside this one.
    # The predicates outside the parentheses are not processed in this listener. It is handled by the child class KeyPrinter in temp.py
    def exitPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        predicate = ctx.predicate().getText()
        if (predicate[0] == "("):
            for i in range(2):
                last_predicate = self.predicate_list.pop()
                if (last_predicate[0] != "("):
                    self.output_predicate.append(last_predicate)
            self.predicate_list.append(predicate)
        else:
            self.predicate_list.append(self.temp_split_list)
            


    # Enter a parse tree produced by frameQLParser#soundsLikePredicate.
    def enterSoundsLikePredicate(self, ctx:frameQLParser.SoundsLikePredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#soundsLikePredicate.
    def exitSoundsLikePredicate(self, ctx:frameQLParser.SoundsLikePredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#expressionAtomPredicate.
    def enterExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#expressionAtomPredicate.
    def exitExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#inPredicate.
    def enterInPredicate(self, ctx:frameQLParser.InPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#inPredicate.
    def exitInPredicate(self, ctx:frameQLParser.InPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#subqueryComparasionPredicate.
    def enterSubqueryComparasionPredicate(self, ctx:frameQLParser.SubqueryComparasionPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#subqueryComparasionPredicate.
    def exitSubqueryComparasionPredicate(self, ctx:frameQLParser.SubqueryComparasionPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#betweenPredicate.
    def enterBetweenPredicate(self, ctx:frameQLParser.BetweenPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#betweenPredicate.
    def exitBetweenPredicate(self, ctx:frameQLParser.BetweenPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#binaryComparasionPredicate.
    def enterBinaryComparasionPredicate(self, ctx:frameQLParser.BinaryComparasionPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#binaryComparasionPredicate.
    # Each predicate is split into a list of expressions and comparason operator
    def exitBinaryComparasionPredicate(self, ctx:frameQLParser.BinaryComparasionPredicateContext):
        self.temp_split_list = []
        self.temp_split_list.append(ctx.predicate(0).getText())
        self.temp_split_list.append(ctx.comparisonOperator().getText())
        self.temp_split_list.append(ctx.predicate(1).getText())


    # Enter a parse tree produced by frameQLParser#isNullPredicate.
    def enterIsNullPredicate(self, ctx:frameQLParser.IsNullPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#isNullPredicate.
    def exitIsNullPredicate(self, ctx:frameQLParser.IsNullPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#likePredicate.
    def enterLikePredicate(self, ctx:frameQLParser.LikePredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#likePredicate.
    def exitLikePredicate(self, ctx:frameQLParser.LikePredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#regexpPredicate.
    def enterRegexpPredicate(self, ctx:frameQLParser.RegexpPredicateContext):
        pass

    # Exit a parse tree produced by frameQLParser#regexpPredicate.
    def exitRegexpPredicate(self, ctx:frameQLParser.RegexpPredicateContext):
        pass


    # Enter a parse tree produced by frameQLParser#unaryExpressionAtom.
    def enterUnaryExpressionAtom(self, ctx:frameQLParser.UnaryExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#unaryExpressionAtom.
    def exitUnaryExpressionAtom(self, ctx:frameQLParser.UnaryExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#collateExpressionAtom.
    def enterCollateExpressionAtom(self, ctx:frameQLParser.CollateExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#collateExpressionAtom.
    def exitCollateExpressionAtom(self, ctx:frameQLParser.CollateExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#subqueryExpessionAtom.
    def enterSubqueryExpessionAtom(self, ctx:frameQLParser.SubqueryExpessionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#subqueryExpessionAtom.
    def exitSubqueryExpessionAtom(self, ctx:frameQLParser.SubqueryExpessionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#mysqlVariableExpressionAtom.
    def enterMysqlVariableExpressionAtom(self, ctx:frameQLParser.MysqlVariableExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#mysqlVariableExpressionAtom.
    def exitMysqlVariableExpressionAtom(self, ctx:frameQLParser.MysqlVariableExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#nestedExpressionAtom.
    def enterNestedExpressionAtom(self, ctx:frameQLParser.NestedExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#nestedExpressionAtom.
    def exitNestedExpressionAtom(self, ctx:frameQLParser.NestedExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#nestedRowExpressionAtom.
    def enterNestedRowExpressionAtom(self, ctx:frameQLParser.NestedRowExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#nestedRowExpressionAtom.
    def exitNestedRowExpressionAtom(self, ctx:frameQLParser.NestedRowExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#mathExpressionAtom.
    def enterMathExpressionAtom(self, ctx:frameQLParser.MathExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#mathExpressionAtom.
    def exitMathExpressionAtom(self, ctx:frameQLParser.MathExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#intervalExpressionAtom.
    def enterIntervalExpressionAtom(self, ctx:frameQLParser.IntervalExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#intervalExpressionAtom.
    def exitIntervalExpressionAtom(self, ctx:frameQLParser.IntervalExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#existsExpessionAtom.
    def enterExistsExpessionAtom(self, ctx:frameQLParser.ExistsExpessionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#existsExpessionAtom.
    def exitExistsExpessionAtom(self, ctx:frameQLParser.ExistsExpessionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#constantExpressionAtom.
    def enterConstantExpressionAtom(self, ctx:frameQLParser.ConstantExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#constantExpressionAtom.
    def exitConstantExpressionAtom(self, ctx:frameQLParser.ConstantExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#functionCallExpressionAtom.
    def enterFunctionCallExpressionAtom(self, ctx:frameQLParser.FunctionCallExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#functionCallExpressionAtom.
    def exitFunctionCallExpressionAtom(self, ctx:frameQLParser.FunctionCallExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#binaryExpressionAtom.
    def enterBinaryExpressionAtom(self, ctx:frameQLParser.BinaryExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#binaryExpressionAtom.
    def exitBinaryExpressionAtom(self, ctx:frameQLParser.BinaryExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#fullColumnNameExpressionAtom.
    def enterFullColumnNameExpressionAtom(self, ctx:frameQLParser.FullColumnNameExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#fullColumnNameExpressionAtom.
    def exitFullColumnNameExpressionAtom(self, ctx:frameQLParser.FullColumnNameExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#bitExpressionAtom.
    def enterBitExpressionAtom(self, ctx:frameQLParser.BitExpressionAtomContext):
        pass

    # Exit a parse tree produced by frameQLParser#bitExpressionAtom.
    def exitBitExpressionAtom(self, ctx:frameQLParser.BitExpressionAtomContext):
        pass


    # Enter a parse tree produced by frameQLParser#unaryOperator.
    def enterUnaryOperator(self, ctx:frameQLParser.UnaryOperatorContext):
        pass

    # Exit a parse tree produced by frameQLParser#unaryOperator.
    def exitUnaryOperator(self, ctx:frameQLParser.UnaryOperatorContext):
        pass


    # Enter a parse tree produced by frameQLParser#comparisonOperator.
    def enterComparisonOperator(self, ctx:frameQLParser.ComparisonOperatorContext):
        pass

    # Exit a parse tree produced by frameQLParser#comparisonOperator.
    def exitComparisonOperator(self, ctx:frameQLParser.ComparisonOperatorContext):
        pass


    # Enter a parse tree produced by frameQLParser#logicalOperator.
    def enterLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        pass

    # Exit a parse tree produced by frameQLParser#logicalOperator.
    def exitLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        pass


    # Enter a parse tree produced by frameQLParser#bitOperator.
    def enterBitOperator(self, ctx:frameQLParser.BitOperatorContext):
        pass

    # Exit a parse tree produced by frameQLParser#bitOperator.
    def exitBitOperator(self, ctx:frameQLParser.BitOperatorContext):
        pass


    # Enter a parse tree produced by frameQLParser#mathOperator.
    def enterMathOperator(self, ctx:frameQLParser.MathOperatorContext):
        pass

    # Exit a parse tree produced by frameQLParser#mathOperator.
    def exitMathOperator(self, ctx:frameQLParser.MathOperatorContext):
        pass


    # Enter a parse tree produced by frameQLParser#charsetNameBase.
    def enterCharsetNameBase(self, ctx:frameQLParser.CharsetNameBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#charsetNameBase.
    def exitCharsetNameBase(self, ctx:frameQLParser.CharsetNameBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#transactionLevelBase.
    def enterTransactionLevelBase(self, ctx:frameQLParser.TransactionLevelBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#transactionLevelBase.
    def exitTransactionLevelBase(self, ctx:frameQLParser.TransactionLevelBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#privilegesBase.
    def enterPrivilegesBase(self, ctx:frameQLParser.PrivilegesBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#privilegesBase.
    def exitPrivilegesBase(self, ctx:frameQLParser.PrivilegesBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#intervalTypeBase.
    def enterIntervalTypeBase(self, ctx:frameQLParser.IntervalTypeBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#intervalTypeBase.
    def exitIntervalTypeBase(self, ctx:frameQLParser.IntervalTypeBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#dataTypeBase.
    def enterDataTypeBase(self, ctx:frameQLParser.DataTypeBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#dataTypeBase.
    def exitDataTypeBase(self, ctx:frameQLParser.DataTypeBaseContext):
        pass


    # Enter a parse tree produced by frameQLParser#keywordsCanBeId.
    def enterKeywordsCanBeId(self, ctx:frameQLParser.KeywordsCanBeIdContext):
        pass

    # Exit a parse tree produced by frameQLParser#keywordsCanBeId.
    def exitKeywordsCanBeId(self, ctx:frameQLParser.KeywordsCanBeIdContext):
        pass


    # Enter a parse tree produced by frameQLParser#functionNameBase.
    def enterFunctionNameBase(self, ctx:frameQLParser.FunctionNameBaseContext):
        pass

    # Exit a parse tree produced by frameQLParser#functionNameBase.
    def exitFunctionNameBase(self, ctx:frameQLParser.FunctionNameBaseContext):
        pass


