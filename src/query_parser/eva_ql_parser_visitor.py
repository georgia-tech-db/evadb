from antlr4 import *
from third_party.evaQL.parser.frameQLParser import frameQLParser
from third_party.evaQL.parser.frameQLParserVisitor import frameQLParserVisitor
from src.query_parser.eva_statement import EvaStatementList
from src.query_parser.select_statement import SelectStatement
from src.expression.logical_expression import LogicalExpression
from src.expression.comparison_expression import ComparisonExpression
from src.expression.abstract_expression import AbstractExpression, ExpressionType
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.tuple_value_expression import TupleValueExpression

class EvaParserVisitor(frameQLParserVisitor):
    # Visit a parse tree produced by frameQLParser#root.
    def visitRoot(self, ctx:frameQLParser.RootContext):
        for child in ctx.children:
            if child is not TerminalNode:
                return self.visit(child)


    # Visit a parse tree produced by frameQLParser#sqlStatements.
    def visitSqlStatements(self, ctx:frameQLParser.SqlStatementsContext):
        eva_statements = EvaStatementList();
        for child in ctx.children:
            stmt = self.visit(child)
            if stmt is not None:
                eva_statements.add_statement(stmt)
        
        return eva_statements

    # Visit a parse tree produced by frameQLParser#sqlStatement.
    def visitSqlStatement(self, ctx:frameQLParser.SqlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#emptyStatement.
    def visitEmptyStatement(self, ctx:frameQLParser.EmptyStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ddlStatement.
    def visitDdlStatement(self, ctx:frameQLParser.DdlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dmlStatement.
    def visitDmlStatement(self, ctx:frameQLParser.DmlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#transactionStatement.
    def visitTransactionStatement(self, ctx:frameQLParser.TransactionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#replicationStatement.
    def visitReplicationStatement(self, ctx:frameQLParser.ReplicationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#preparedStatement.
    def visitPreparedStatement(self, ctx:frameQLParser.PreparedStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#compoundStatement.
    def visitCompoundStatement(self, ctx:frameQLParser.CompoundStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#administrationStatement.
    def visitAdministrationStatement(self, ctx:frameQLParser.AdministrationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#utilityStatement.
    def visitUtilityStatement(self, ctx:frameQLParser.UtilityStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createDatabase.
    def visitCreateDatabase(self, ctx:frameQLParser.CreateDatabaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createEvent.
    def visitCreateEvent(self, ctx:frameQLParser.CreateEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createIndex.
    def visitCreateIndex(self, ctx:frameQLParser.CreateIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createLogfileGroup.
    def visitCreateLogfileGroup(self, ctx:frameQLParser.CreateLogfileGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createProcedure.
    def visitCreateProcedure(self, ctx:frameQLParser.CreateProcedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createFunction.
    def visitCreateFunction(self, ctx:frameQLParser.CreateFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createServer.
    def visitCreateServer(self, ctx:frameQLParser.CreateServerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#copyCreateTable.
    def visitCopyCreateTable(self, ctx:frameQLParser.CopyCreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#queryCreateTable.
    def visitQueryCreateTable(self, ctx:frameQLParser.QueryCreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#columnCreateTable.
    def visitColumnCreateTable(self, ctx:frameQLParser.ColumnCreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createTablespaceInnodb.
    def visitCreateTablespaceInnodb(self, ctx:frameQLParser.CreateTablespaceInnodbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createTablespaceNdb.
    def visitCreateTablespaceNdb(self, ctx:frameQLParser.CreateTablespaceNdbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createTrigger.
    def visitCreateTrigger(self, ctx:frameQLParser.CreateTriggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createView.
    def visitCreateView(self, ctx:frameQLParser.CreateViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createDatabaseOption.
    def visitCreateDatabaseOption(self, ctx:frameQLParser.CreateDatabaseOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ownerStatement.
    def visitOwnerStatement(self, ctx:frameQLParser.OwnerStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#preciseSchedule.
    def visitPreciseSchedule(self, ctx:frameQLParser.PreciseScheduleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#intervalSchedule.
    def visitIntervalSchedule(self, ctx:frameQLParser.IntervalScheduleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#timestampValue.
    def visitTimestampValue(self, ctx:frameQLParser.TimestampValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#intervalExpr.
    def visitIntervalExpr(self, ctx:frameQLParser.IntervalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#intervalType.
    def visitIntervalType(self, ctx:frameQLParser.IntervalTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#enableType.
    def visitEnableType(self, ctx:frameQLParser.EnableTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexType.
    def visitIndexType(self, ctx:frameQLParser.IndexTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexOption.
    def visitIndexOption(self, ctx:frameQLParser.IndexOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#procedureParameter.
    def visitProcedureParameter(self, ctx:frameQLParser.ProcedureParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#functionParameter.
    def visitFunctionParameter(self, ctx:frameQLParser.FunctionParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineComment.
    def visitRoutineComment(self, ctx:frameQLParser.RoutineCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineLanguage.
    def visitRoutineLanguage(self, ctx:frameQLParser.RoutineLanguageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineBehavior.
    def visitRoutineBehavior(self, ctx:frameQLParser.RoutineBehaviorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineData.
    def visitRoutineData(self, ctx:frameQLParser.RoutineDataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineSecurity.
    def visitRoutineSecurity(self, ctx:frameQLParser.RoutineSecurityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#serverOption.
    def visitServerOption(self, ctx:frameQLParser.ServerOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createDefinitions.
    def visitCreateDefinitions(self, ctx:frameQLParser.CreateDefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#columnDeclaration.
    def visitColumnDeclaration(self, ctx:frameQLParser.ColumnDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#constraintDeclaration.
    def visitConstraintDeclaration(self, ctx:frameQLParser.ConstraintDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexDeclaration.
    def visitIndexDeclaration(self, ctx:frameQLParser.IndexDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#columnDefinition.
    def visitColumnDefinition(self, ctx:frameQLParser.ColumnDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#nullColumnConstraint.
    def visitNullColumnConstraint(self, ctx:frameQLParser.NullColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#defaultColumnConstraint.
    def visitDefaultColumnConstraint(self, ctx:frameQLParser.DefaultColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#autoIncrementColumnConstraint.
    def visitAutoIncrementColumnConstraint(self, ctx:frameQLParser.AutoIncrementColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#primaryKeyColumnConstraint.
    def visitPrimaryKeyColumnConstraint(self, ctx:frameQLParser.PrimaryKeyColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uniqueKeyColumnConstraint.
    def visitUniqueKeyColumnConstraint(self, ctx:frameQLParser.UniqueKeyColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#commentColumnConstraint.
    def visitCommentColumnConstraint(self, ctx:frameQLParser.CommentColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#formatColumnConstraint.
    def visitFormatColumnConstraint(self, ctx:frameQLParser.FormatColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#storageColumnConstraint.
    def visitStorageColumnConstraint(self, ctx:frameQLParser.StorageColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#referenceColumnConstraint.
    def visitReferenceColumnConstraint(self, ctx:frameQLParser.ReferenceColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#generatedColumnConstraint.
    def visitGeneratedColumnConstraint(self, ctx:frameQLParser.GeneratedColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#serialDefaultColumnConstraint.
    def visitSerialDefaultColumnConstraint(self, ctx:frameQLParser.SerialDefaultColumnConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#primaryKeyTableConstraint.
    def visitPrimaryKeyTableConstraint(self, ctx:frameQLParser.PrimaryKeyTableConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uniqueKeyTableConstraint.
    def visitUniqueKeyTableConstraint(self, ctx:frameQLParser.UniqueKeyTableConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#foreignKeyTableConstraint.
    def visitForeignKeyTableConstraint(self, ctx:frameQLParser.ForeignKeyTableConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#checkTableConstraint.
    def visitCheckTableConstraint(self, ctx:frameQLParser.CheckTableConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#referenceDefinition.
    def visitReferenceDefinition(self, ctx:frameQLParser.ReferenceDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#referenceAction.
    def visitReferenceAction(self, ctx:frameQLParser.ReferenceActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#referenceControlType.
    def visitReferenceControlType(self, ctx:frameQLParser.ReferenceControlTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleIndexDeclaration.
    def visitSimpleIndexDeclaration(self, ctx:frameQLParser.SimpleIndexDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#specialIndexDeclaration.
    def visitSpecialIndexDeclaration(self, ctx:frameQLParser.SpecialIndexDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionEngine.
    def visitTableOptionEngine(self, ctx:frameQLParser.TableOptionEngineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionAutoIncrement.
    def visitTableOptionAutoIncrement(self, ctx:frameQLParser.TableOptionAutoIncrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionAverage.
    def visitTableOptionAverage(self, ctx:frameQLParser.TableOptionAverageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionCharset.
    def visitTableOptionCharset(self, ctx:frameQLParser.TableOptionCharsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionChecksum.
    def visitTableOptionChecksum(self, ctx:frameQLParser.TableOptionChecksumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionCollate.
    def visitTableOptionCollate(self, ctx:frameQLParser.TableOptionCollateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionComment.
    def visitTableOptionComment(self, ctx:frameQLParser.TableOptionCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionCompression.
    def visitTableOptionCompression(self, ctx:frameQLParser.TableOptionCompressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionConnection.
    def visitTableOptionConnection(self, ctx:frameQLParser.TableOptionConnectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionDataDirectory.
    def visitTableOptionDataDirectory(self, ctx:frameQLParser.TableOptionDataDirectoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionDelay.
    def visitTableOptionDelay(self, ctx:frameQLParser.TableOptionDelayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionEncryption.
    def visitTableOptionEncryption(self, ctx:frameQLParser.TableOptionEncryptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionIndexDirectory.
    def visitTableOptionIndexDirectory(self, ctx:frameQLParser.TableOptionIndexDirectoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionInsertMethod.
    def visitTableOptionInsertMethod(self, ctx:frameQLParser.TableOptionInsertMethodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionKeyBlockSize.
    def visitTableOptionKeyBlockSize(self, ctx:frameQLParser.TableOptionKeyBlockSizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionMaxRows.
    def visitTableOptionMaxRows(self, ctx:frameQLParser.TableOptionMaxRowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionMinRows.
    def visitTableOptionMinRows(self, ctx:frameQLParser.TableOptionMinRowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionPackKeys.
    def visitTableOptionPackKeys(self, ctx:frameQLParser.TableOptionPackKeysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionPassword.
    def visitTableOptionPassword(self, ctx:frameQLParser.TableOptionPasswordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionRowFormat.
    def visitTableOptionRowFormat(self, ctx:frameQLParser.TableOptionRowFormatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionRecalculation.
    def visitTableOptionRecalculation(self, ctx:frameQLParser.TableOptionRecalculationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionPersistent.
    def visitTableOptionPersistent(self, ctx:frameQLParser.TableOptionPersistentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionSamplePage.
    def visitTableOptionSamplePage(self, ctx:frameQLParser.TableOptionSamplePageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionTablespace.
    def visitTableOptionTablespace(self, ctx:frameQLParser.TableOptionTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableOptionUnion.
    def visitTableOptionUnion(self, ctx:frameQLParser.TableOptionUnionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tablespaceStorage.
    def visitTablespaceStorage(self, ctx:frameQLParser.TablespaceStorageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionDefinitions.
    def visitPartitionDefinitions(self, ctx:frameQLParser.PartitionDefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionFunctionHash.
    def visitPartitionFunctionHash(self, ctx:frameQLParser.PartitionFunctionHashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionFunctionKey.
    def visitPartitionFunctionKey(self, ctx:frameQLParser.PartitionFunctionKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionFunctionRange.
    def visitPartitionFunctionRange(self, ctx:frameQLParser.PartitionFunctionRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionFunctionList.
    def visitPartitionFunctionList(self, ctx:frameQLParser.PartitionFunctionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subPartitionFunctionHash.
    def visitSubPartitionFunctionHash(self, ctx:frameQLParser.SubPartitionFunctionHashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subPartitionFunctionKey.
    def visitSubPartitionFunctionKey(self, ctx:frameQLParser.SubPartitionFunctionKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionComparision.
    def visitPartitionComparision(self, ctx:frameQLParser.PartitionComparisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionListAtom.
    def visitPartitionListAtom(self, ctx:frameQLParser.PartitionListAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionListVector.
    def visitPartitionListVector(self, ctx:frameQLParser.PartitionListVectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionSimple.
    def visitPartitionSimple(self, ctx:frameQLParser.PartitionSimpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionDefinerAtom.
    def visitPartitionDefinerAtom(self, ctx:frameQLParser.PartitionDefinerAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionDefinerVector.
    def visitPartitionDefinerVector(self, ctx:frameQLParser.PartitionDefinerVectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subpartitionDefinition.
    def visitSubpartitionDefinition(self, ctx:frameQLParser.SubpartitionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionEngine.
    def visitPartitionOptionEngine(self, ctx:frameQLParser.PartitionOptionEngineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionComment.
    def visitPartitionOptionComment(self, ctx:frameQLParser.PartitionOptionCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionDataDirectory.
    def visitPartitionOptionDataDirectory(self, ctx:frameQLParser.PartitionOptionDataDirectoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionIndexDirectory.
    def visitPartitionOptionIndexDirectory(self, ctx:frameQLParser.PartitionOptionIndexDirectoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionMaxRows.
    def visitPartitionOptionMaxRows(self, ctx:frameQLParser.PartitionOptionMaxRowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionMinRows.
    def visitPartitionOptionMinRows(self, ctx:frameQLParser.PartitionOptionMinRowsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionTablespace.
    def visitPartitionOptionTablespace(self, ctx:frameQLParser.PartitionOptionTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#partitionOptionNodeGroup.
    def visitPartitionOptionNodeGroup(self, ctx:frameQLParser.PartitionOptionNodeGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterSimpleDatabase.
    def visitAlterSimpleDatabase(self, ctx:frameQLParser.AlterSimpleDatabaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterUpgradeName.
    def visitAlterUpgradeName(self, ctx:frameQLParser.AlterUpgradeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterEvent.
    def visitAlterEvent(self, ctx:frameQLParser.AlterEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterFunction.
    def visitAlterFunction(self, ctx:frameQLParser.AlterFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterInstance.
    def visitAlterInstance(self, ctx:frameQLParser.AlterInstanceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterLogfileGroup.
    def visitAlterLogfileGroup(self, ctx:frameQLParser.AlterLogfileGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterProcedure.
    def visitAlterProcedure(self, ctx:frameQLParser.AlterProcedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterServer.
    def visitAlterServer(self, ctx:frameQLParser.AlterServerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterTable.
    def visitAlterTable(self, ctx:frameQLParser.AlterTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterTablespace.
    def visitAlterTablespace(self, ctx:frameQLParser.AlterTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterView.
    def visitAlterView(self, ctx:frameQLParser.AlterViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByTableOption.
    def visitAlterByTableOption(self, ctx:frameQLParser.AlterByTableOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddColumn.
    def visitAlterByAddColumn(self, ctx:frameQLParser.AlterByAddColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddColumns.
    def visitAlterByAddColumns(self, ctx:frameQLParser.AlterByAddColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddIndex.
    def visitAlterByAddIndex(self, ctx:frameQLParser.AlterByAddIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddPrimaryKey.
    def visitAlterByAddPrimaryKey(self, ctx:frameQLParser.AlterByAddPrimaryKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddUniqueKey.
    def visitAlterByAddUniqueKey(self, ctx:frameQLParser.AlterByAddUniqueKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddSpecialIndex.
    def visitAlterByAddSpecialIndex(self, ctx:frameQLParser.AlterByAddSpecialIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddForeignKey.
    def visitAlterByAddForeignKey(self, ctx:frameQLParser.AlterByAddForeignKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddCheckTableConstraint.
    def visitAlterByAddCheckTableConstraint(self, ctx:frameQLParser.AlterByAddCheckTableConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterBySetAlgorithm.
    def visitAlterBySetAlgorithm(self, ctx:frameQLParser.AlterBySetAlgorithmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByChangeDefault.
    def visitAlterByChangeDefault(self, ctx:frameQLParser.AlterByChangeDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByChangeColumn.
    def visitAlterByChangeColumn(self, ctx:frameQLParser.AlterByChangeColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByRenameColumn.
    def visitAlterByRenameColumn(self, ctx:frameQLParser.AlterByRenameColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByLock.
    def visitAlterByLock(self, ctx:frameQLParser.AlterByLockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByModifyColumn.
    def visitAlterByModifyColumn(self, ctx:frameQLParser.AlterByModifyColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDropColumn.
    def visitAlterByDropColumn(self, ctx:frameQLParser.AlterByDropColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDropPrimaryKey.
    def visitAlterByDropPrimaryKey(self, ctx:frameQLParser.AlterByDropPrimaryKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDropIndex.
    def visitAlterByDropIndex(self, ctx:frameQLParser.AlterByDropIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDropForeignKey.
    def visitAlterByDropForeignKey(self, ctx:frameQLParser.AlterByDropForeignKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDisableKeys.
    def visitAlterByDisableKeys(self, ctx:frameQLParser.AlterByDisableKeysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByEnableKeys.
    def visitAlterByEnableKeys(self, ctx:frameQLParser.AlterByEnableKeysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByRename.
    def visitAlterByRename(self, ctx:frameQLParser.AlterByRenameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByOrder.
    def visitAlterByOrder(self, ctx:frameQLParser.AlterByOrderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByConvertCharset.
    def visitAlterByConvertCharset(self, ctx:frameQLParser.AlterByConvertCharsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDefaultCharset.
    def visitAlterByDefaultCharset(self, ctx:frameQLParser.AlterByDefaultCharsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDiscardTablespace.
    def visitAlterByDiscardTablespace(self, ctx:frameQLParser.AlterByDiscardTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByImportTablespace.
    def visitAlterByImportTablespace(self, ctx:frameQLParser.AlterByImportTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByForce.
    def visitAlterByForce(self, ctx:frameQLParser.AlterByForceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByValidate.
    def visitAlterByValidate(self, ctx:frameQLParser.AlterByValidateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAddPartition.
    def visitAlterByAddPartition(self, ctx:frameQLParser.AlterByAddPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDropPartition.
    def visitAlterByDropPartition(self, ctx:frameQLParser.AlterByDropPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByDiscardPartition.
    def visitAlterByDiscardPartition(self, ctx:frameQLParser.AlterByDiscardPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByImportPartition.
    def visitAlterByImportPartition(self, ctx:frameQLParser.AlterByImportPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByTruncatePartition.
    def visitAlterByTruncatePartition(self, ctx:frameQLParser.AlterByTruncatePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByCoalescePartition.
    def visitAlterByCoalescePartition(self, ctx:frameQLParser.AlterByCoalescePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByReorganizePartition.
    def visitAlterByReorganizePartition(self, ctx:frameQLParser.AlterByReorganizePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByExchangePartition.
    def visitAlterByExchangePartition(self, ctx:frameQLParser.AlterByExchangePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByAnalyzePartitiion.
    def visitAlterByAnalyzePartitiion(self, ctx:frameQLParser.AlterByAnalyzePartitiionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByCheckPartition.
    def visitAlterByCheckPartition(self, ctx:frameQLParser.AlterByCheckPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByOptimizePartition.
    def visitAlterByOptimizePartition(self, ctx:frameQLParser.AlterByOptimizePartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByRebuildPartition.
    def visitAlterByRebuildPartition(self, ctx:frameQLParser.AlterByRebuildPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByRepairPartition.
    def visitAlterByRepairPartition(self, ctx:frameQLParser.AlterByRepairPartitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByRemovePartitioning.
    def visitAlterByRemovePartitioning(self, ctx:frameQLParser.AlterByRemovePartitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterByUpgradePartitioning.
    def visitAlterByUpgradePartitioning(self, ctx:frameQLParser.AlterByUpgradePartitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropDatabase.
    def visitDropDatabase(self, ctx:frameQLParser.DropDatabaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropEvent.
    def visitDropEvent(self, ctx:frameQLParser.DropEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropIndex.
    def visitDropIndex(self, ctx:frameQLParser.DropIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropLogfileGroup.
    def visitDropLogfileGroup(self, ctx:frameQLParser.DropLogfileGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropProcedure.
    def visitDropProcedure(self, ctx:frameQLParser.DropProcedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropFunction.
    def visitDropFunction(self, ctx:frameQLParser.DropFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropServer.
    def visitDropServer(self, ctx:frameQLParser.DropServerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropTable.
    def visitDropTable(self, ctx:frameQLParser.DropTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropTablespace.
    def visitDropTablespace(self, ctx:frameQLParser.DropTablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropTrigger.
    def visitDropTrigger(self, ctx:frameQLParser.DropTriggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropView.
    def visitDropView(self, ctx:frameQLParser.DropViewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#renameTable.
    def visitRenameTable(self, ctx:frameQLParser.RenameTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#renameTableClause.
    def visitRenameTableClause(self, ctx:frameQLParser.RenameTableClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#truncateTable.
    def visitTruncateTable(self, ctx:frameQLParser.TruncateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#callStatement.
    def visitCallStatement(self, ctx:frameQLParser.CallStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#deleteStatement.
    def visitDeleteStatement(self, ctx:frameQLParser.DeleteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#doStatement.
    def visitDoStatement(self, ctx:frameQLParser.DoStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerStatement.
    def visitHandlerStatement(self, ctx:frameQLParser.HandlerStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#insertStatement.
    def visitInsertStatement(self, ctx:frameQLParser.InsertStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#loadDataStatement.
    def visitLoadDataStatement(self, ctx:frameQLParser.LoadDataStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#loadXmlStatement.
    def visitLoadXmlStatement(self, ctx:frameQLParser.LoadXmlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#replaceStatement.
    def visitReplaceStatement(self, ctx:frameQLParser.ReplaceStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleSelect.
    def visitSimpleSelect(self, ctx:frameQLParser.SimpleSelectContext):
        select_stm = self.visitChildren(ctx)
        return select_stm

    # Visit a parse tree produced by frameQLParser#parenthesisSelect.
    def visitParenthesisSelect(self, ctx:frameQLParser.ParenthesisSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unionSelect.
    def visitUnionSelect(self, ctx:frameQLParser.UnionSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unionParenthesisSelect.
    def visitUnionParenthesisSelect(self, ctx:frameQLParser.UnionParenthesisSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#updateStatement.
    def visitUpdateStatement(self, ctx:frameQLParser.UpdateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#insertStatementValue.
    def visitInsertStatementValue(self, ctx:frameQLParser.InsertStatementValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#updatedElement.
    def visitUpdatedElement(self, ctx:frameQLParser.UpdatedElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#assignmentField.
    def visitAssignmentField(self, ctx:frameQLParser.AssignmentFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lockClause.
    def visitLockClause(self, ctx:frameQLParser.LockClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#singleDeleteStatement.
    def visitSingleDeleteStatement(self, ctx:frameQLParser.SingleDeleteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#multipleDeleteStatement.
    def visitMultipleDeleteStatement(self, ctx:frameQLParser.MultipleDeleteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerOpenStatement.
    def visitHandlerOpenStatement(self, ctx:frameQLParser.HandlerOpenStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerReadIndexStatement.
    def visitHandlerReadIndexStatement(self, ctx:frameQLParser.HandlerReadIndexStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerReadStatement.
    def visitHandlerReadStatement(self, ctx:frameQLParser.HandlerReadStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerCloseStatement.
    def visitHandlerCloseStatement(self, ctx:frameQLParser.HandlerCloseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#singleUpdateStatement.
    def visitSingleUpdateStatement(self, ctx:frameQLParser.SingleUpdateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#multipleUpdateStatement.
    def visitMultipleUpdateStatement(self, ctx:frameQLParser.MultipleUpdateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#orderByClause.
    def visitOrderByClause(self, ctx:frameQLParser.OrderByClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#orderByExpression.
    def visitOrderByExpression(self, ctx:frameQLParser.OrderByExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableSources.
    def visitTableSources(self, ctx:frameQLParser.TableSourcesContext):
        table_list = []
        for child in ctx.children:
            table = self.visit(child)
            if table is not None:
                table_list.append(table)
        return table_list


    # Visit a parse tree produced by frameQLParser#tableSourceBase.
    def visitTableSourceBase(self, ctx:frameQLParser.TableSourceBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableSourceNested.
    def visitTableSourceNested(self, ctx:frameQLParser.TableSourceNestedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#atomTableItem.
    def visitAtomTableItem(self, ctx:frameQLParser.AtomTableItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subqueryTableItem.
    def visitSubqueryTableItem(self, ctx:frameQLParser.SubqueryTableItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableSourcesItem.
    def visitTableSourcesItem(self, ctx:frameQLParser.TableSourcesItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexHint.
    def visitIndexHint(self, ctx:frameQLParser.IndexHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexHintType.
    def visitIndexHintType(self, ctx:frameQLParser.IndexHintTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#innerJoin.
    def visitInnerJoin(self, ctx:frameQLParser.InnerJoinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#straightJoin.
    def visitStraightJoin(self, ctx:frameQLParser.StraightJoinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#outerJoin.
    def visitOuterJoin(self, ctx:frameQLParser.OuterJoinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#naturalJoin.
    def visitNaturalJoin(self, ctx:frameQLParser.NaturalJoinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#queryExpression.
    def visitQueryExpression(self, ctx:frameQLParser.QueryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#queryExpressionNointo.
    def visitQueryExpressionNointo(self, ctx:frameQLParser.QueryExpressionNointoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#querySpecification.
    def visitQuerySpecification(self, ctx:frameQLParser.QuerySpecificationContext):
        select_list = None
        from_clause = None
        where_clause = None
        #first child will be a SELECT terminal token
        for child in ctx.children[1:]:
            try:
                rule_idx = child.getRuleIndex()
                if rule_idx == frameQLParser.RULE_selectElements:
                    target_list = self.visit(child)

                elif rule_idx == frameQLParser.RULE_fromClause:
                    clause = self.visit(child) 
                    from_clause = clause.get('from', None)
                    where_clause = clause.get('where', None)
            except:
                #stop parsing something bad happened
                return None

        select_stmt = SelectStatement(target_list, from_clause, where_clause)
        return select_stmt

    # Visit a parse tree produced by frameQLParser#querySpecificationNointo.
    def visitQuerySpecificationNointo(self, ctx:frameQLParser.QuerySpecificationNointoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unionParenthesis.
    def visitUnionParenthesis(self, ctx:frameQLParser.UnionParenthesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unionStatement.
    def visitUnionStatement(self, ctx:frameQLParser.UnionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectSpec.
    def visitSelectSpec(self, ctx:frameQLParser.SelectSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectElements.
    def visitSelectElements(self, ctx:frameQLParser.SelectElementsContext):
        select_list = []
        for child in ctx.children:
            element = self.visit(child)
            if element is not None:
                select_list.append(element)

        return select_list

    # Visit a parse tree produced by frameQLParser#selectStarElement.
    def visitSelectStarElement(self, ctx:frameQLParser.SelectStarElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectColumnElement.
    def visitSelectColumnElement(self, ctx:frameQLParser.SelectColumnElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectFunctionElement.
    def visitSelectFunctionElement(self, ctx:frameQLParser.SelectFunctionElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectExpressionElement.
    def visitSelectExpressionElement(self, ctx:frameQLParser.SelectExpressionElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#errorTolerenceExpression.
    def visitErrorTolerenceExpression(self, ctx:frameQLParser.ErrorTolerenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#confLevelExpression.
    def visitConfLevelExpression(self, ctx:frameQLParser.ConfLevelExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectIntoVariables.
    def visitSelectIntoVariables(self, ctx:frameQLParser.SelectIntoVariablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectIntoDumpFile.
    def visitSelectIntoDumpFile(self, ctx:frameQLParser.SelectIntoDumpFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectIntoTextFile.
    def visitSelectIntoTextFile(self, ctx:frameQLParser.SelectIntoTextFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectFieldsInto.
    def visitSelectFieldsInto(self, ctx:frameQLParser.SelectFieldsIntoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#selectLinesInto.
    def visitSelectLinesInto(self, ctx:frameQLParser.SelectLinesIntoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#fromClause.
    def visitFromClause(self, ctx:frameQLParser.FromClauseContext):
        from_table = None
        where_clause = None

        if ctx.tableSources():
            from_table = self.visit(ctx.tableSources())
        if ctx.whereExpr is not None:
            where_clause = self.visit(ctx.whereExpr)
        
        return {"from" : from_table, "where": where_clause}


    # Visit a parse tree produced by frameQLParser#groupByItem.
    def visitGroupByItem(self, ctx:frameQLParser.GroupByItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#limitClause.
    def visitLimitClause(self, ctx:frameQLParser.LimitClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#startTransaction.
    def visitStartTransaction(self, ctx:frameQLParser.StartTransactionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#beginWork.
    def visitBeginWork(self, ctx:frameQLParser.BeginWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#commitWork.
    def visitCommitWork(self, ctx:frameQLParser.CommitWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#rollbackWork.
    def visitRollbackWork(self, ctx:frameQLParser.RollbackWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#savepointStatement.
    def visitSavepointStatement(self, ctx:frameQLParser.SavepointStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#rollbackStatement.
    def visitRollbackStatement(self, ctx:frameQLParser.RollbackStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#releaseStatement.
    def visitReleaseStatement(self, ctx:frameQLParser.ReleaseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lockTables.
    def visitLockTables(self, ctx:frameQLParser.LockTablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unlockTables.
    def visitUnlockTables(self, ctx:frameQLParser.UnlockTablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setAutocommitStatement.
    def visitSetAutocommitStatement(self, ctx:frameQLParser.SetAutocommitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setTransactionStatement.
    def visitSetTransactionStatement(self, ctx:frameQLParser.SetTransactionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#transactionMode.
    def visitTransactionMode(self, ctx:frameQLParser.TransactionModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lockTableElement.
    def visitLockTableElement(self, ctx:frameQLParser.LockTableElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lockAction.
    def visitLockAction(self, ctx:frameQLParser.LockActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#transactionOption.
    def visitTransactionOption(self, ctx:frameQLParser.TransactionOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#transactionLevel.
    def visitTransactionLevel(self, ctx:frameQLParser.TransactionLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#changeMaster.
    def visitChangeMaster(self, ctx:frameQLParser.ChangeMasterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#changeReplicationFilter.
    def visitChangeReplicationFilter(self, ctx:frameQLParser.ChangeReplicationFilterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#purgeBinaryLogs.
    def visitPurgeBinaryLogs(self, ctx:frameQLParser.PurgeBinaryLogsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#resetMaster.
    def visitResetMaster(self, ctx:frameQLParser.ResetMasterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#resetSlave.
    def visitResetSlave(self, ctx:frameQLParser.ResetSlaveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#startSlave.
    def visitStartSlave(self, ctx:frameQLParser.StartSlaveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stopSlave.
    def visitStopSlave(self, ctx:frameQLParser.StopSlaveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#startGroupReplication.
    def visitStartGroupReplication(self, ctx:frameQLParser.StartGroupReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stopGroupReplication.
    def visitStopGroupReplication(self, ctx:frameQLParser.StopGroupReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterStringOption.
    def visitMasterStringOption(self, ctx:frameQLParser.MasterStringOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterDecimalOption.
    def visitMasterDecimalOption(self, ctx:frameQLParser.MasterDecimalOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterBoolOption.
    def visitMasterBoolOption(self, ctx:frameQLParser.MasterBoolOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterRealOption.
    def visitMasterRealOption(self, ctx:frameQLParser.MasterRealOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterUidListOption.
    def visitMasterUidListOption(self, ctx:frameQLParser.MasterUidListOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stringMasterOption.
    def visitStringMasterOption(self, ctx:frameQLParser.StringMasterOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#decimalMasterOption.
    def visitDecimalMasterOption(self, ctx:frameQLParser.DecimalMasterOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#boolMasterOption.
    def visitBoolMasterOption(self, ctx:frameQLParser.BoolMasterOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#channelOption.
    def visitChannelOption(self, ctx:frameQLParser.ChannelOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#doDbReplication.
    def visitDoDbReplication(self, ctx:frameQLParser.DoDbReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ignoreDbReplication.
    def visitIgnoreDbReplication(self, ctx:frameQLParser.IgnoreDbReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#doTableReplication.
    def visitDoTableReplication(self, ctx:frameQLParser.DoTableReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ignoreTableReplication.
    def visitIgnoreTableReplication(self, ctx:frameQLParser.IgnoreTableReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#wildDoTableReplication.
    def visitWildDoTableReplication(self, ctx:frameQLParser.WildDoTableReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#wildIgnoreTableReplication.
    def visitWildIgnoreTableReplication(self, ctx:frameQLParser.WildIgnoreTableReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#rewriteDbReplication.
    def visitRewriteDbReplication(self, ctx:frameQLParser.RewriteDbReplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tablePair.
    def visitTablePair(self, ctx:frameQLParser.TablePairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#threadType.
    def visitThreadType(self, ctx:frameQLParser.ThreadTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#gtidsUntilOption.
    def visitGtidsUntilOption(self, ctx:frameQLParser.GtidsUntilOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#masterLogUntilOption.
    def visitMasterLogUntilOption(self, ctx:frameQLParser.MasterLogUntilOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#relayLogUntilOption.
    def visitRelayLogUntilOption(self, ctx:frameQLParser.RelayLogUntilOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#sqlGapsUntilOption.
    def visitSqlGapsUntilOption(self, ctx:frameQLParser.SqlGapsUntilOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userConnectionOption.
    def visitUserConnectionOption(self, ctx:frameQLParser.UserConnectionOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#passwordConnectionOption.
    def visitPasswordConnectionOption(self, ctx:frameQLParser.PasswordConnectionOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#defaultAuthConnectionOption.
    def visitDefaultAuthConnectionOption(self, ctx:frameQLParser.DefaultAuthConnectionOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#pluginDirConnectionOption.
    def visitPluginDirConnectionOption(self, ctx:frameQLParser.PluginDirConnectionOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#gtuidSet.
    def visitGtuidSet(self, ctx:frameQLParser.GtuidSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaStartTransaction.
    def visitXaStartTransaction(self, ctx:frameQLParser.XaStartTransactionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaEndTransaction.
    def visitXaEndTransaction(self, ctx:frameQLParser.XaEndTransactionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaPrepareStatement.
    def visitXaPrepareStatement(self, ctx:frameQLParser.XaPrepareStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaCommitWork.
    def visitXaCommitWork(self, ctx:frameQLParser.XaCommitWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaRollbackWork.
    def visitXaRollbackWork(self, ctx:frameQLParser.XaRollbackWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xaRecoverWork.
    def visitXaRecoverWork(self, ctx:frameQLParser.XaRecoverWorkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#prepareStatement.
    def visitPrepareStatement(self, ctx:frameQLParser.PrepareStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#executeStatement.
    def visitExecuteStatement(self, ctx:frameQLParser.ExecuteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#deallocatePrepare.
    def visitDeallocatePrepare(self, ctx:frameQLParser.DeallocatePrepareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#routineBody.
    def visitRoutineBody(self, ctx:frameQLParser.RoutineBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#blockStatement.
    def visitBlockStatement(self, ctx:frameQLParser.BlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#caseStatement.
    def visitCaseStatement(self, ctx:frameQLParser.CaseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ifStatement.
    def visitIfStatement(self, ctx:frameQLParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#iterateStatement.
    def visitIterateStatement(self, ctx:frameQLParser.IterateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#leaveStatement.
    def visitLeaveStatement(self, ctx:frameQLParser.LeaveStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#loopStatement.
    def visitLoopStatement(self, ctx:frameQLParser.LoopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#repeatStatement.
    def visitRepeatStatement(self, ctx:frameQLParser.RepeatStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#returnStatement.
    def visitReturnStatement(self, ctx:frameQLParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#whileStatement.
    def visitWhileStatement(self, ctx:frameQLParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#CloseCursor.
    def visitCloseCursor(self, ctx:frameQLParser.CloseCursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#FetchCursor.
    def visitFetchCursor(self, ctx:frameQLParser.FetchCursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#OpenCursor.
    def visitOpenCursor(self, ctx:frameQLParser.OpenCursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#declareVariable.
    def visitDeclareVariable(self, ctx:frameQLParser.DeclareVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#declareCondition.
    def visitDeclareCondition(self, ctx:frameQLParser.DeclareConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#declareCursor.
    def visitDeclareCursor(self, ctx:frameQLParser.DeclareCursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#declareHandler.
    def visitDeclareHandler(self, ctx:frameQLParser.DeclareHandlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionCode.
    def visitHandlerConditionCode(self, ctx:frameQLParser.HandlerConditionCodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionState.
    def visitHandlerConditionState(self, ctx:frameQLParser.HandlerConditionStateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionName.
    def visitHandlerConditionName(self, ctx:frameQLParser.HandlerConditionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionWarning.
    def visitHandlerConditionWarning(self, ctx:frameQLParser.HandlerConditionWarningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionNotfound.
    def visitHandlerConditionNotfound(self, ctx:frameQLParser.HandlerConditionNotfoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#handlerConditionException.
    def visitHandlerConditionException(self, ctx:frameQLParser.HandlerConditionExceptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#procedureSqlStatement.
    def visitProcedureSqlStatement(self, ctx:frameQLParser.ProcedureSqlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#caseAlternative.
    def visitCaseAlternative(self, ctx:frameQLParser.CaseAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#elifAlternative.
    def visitElifAlternative(self, ctx:frameQLParser.ElifAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterUserMysqlV56.
    def visitAlterUserMysqlV56(self, ctx:frameQLParser.AlterUserMysqlV56Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#alterUserMysqlV57.
    def visitAlterUserMysqlV57(self, ctx:frameQLParser.AlterUserMysqlV57Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createUserMysqlV56.
    def visitCreateUserMysqlV56(self, ctx:frameQLParser.CreateUserMysqlV56Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createUserMysqlV57.
    def visitCreateUserMysqlV57(self, ctx:frameQLParser.CreateUserMysqlV57Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dropUser.
    def visitDropUser(self, ctx:frameQLParser.DropUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#grantStatement.
    def visitGrantStatement(self, ctx:frameQLParser.GrantStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#grantProxy.
    def visitGrantProxy(self, ctx:frameQLParser.GrantProxyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#renameUser.
    def visitRenameUser(self, ctx:frameQLParser.RenameUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#detailRevoke.
    def visitDetailRevoke(self, ctx:frameQLParser.DetailRevokeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#shortRevoke.
    def visitShortRevoke(self, ctx:frameQLParser.ShortRevokeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#revokeProxy.
    def visitRevokeProxy(self, ctx:frameQLParser.RevokeProxyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setPasswordStatement.
    def visitSetPasswordStatement(self, ctx:frameQLParser.SetPasswordStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userSpecification.
    def visitUserSpecification(self, ctx:frameQLParser.UserSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#passwordAuthOption.
    def visitPasswordAuthOption(self, ctx:frameQLParser.PasswordAuthOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stringAuthOption.
    def visitStringAuthOption(self, ctx:frameQLParser.StringAuthOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#hashAuthOption.
    def visitHashAuthOption(self, ctx:frameQLParser.HashAuthOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleAuthOption.
    def visitSimpleAuthOption(self, ctx:frameQLParser.SimpleAuthOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tlsOption.
    def visitTlsOption(self, ctx:frameQLParser.TlsOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userResourceOption.
    def visitUserResourceOption(self, ctx:frameQLParser.UserResourceOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userPasswordOption.
    def visitUserPasswordOption(self, ctx:frameQLParser.UserPasswordOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userLockOption.
    def visitUserLockOption(self, ctx:frameQLParser.UserLockOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#privelegeClause.
    def visitPrivelegeClause(self, ctx:frameQLParser.PrivelegeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#privilege.
    def visitPrivilege(self, ctx:frameQLParser.PrivilegeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#currentSchemaPriviLevel.
    def visitCurrentSchemaPriviLevel(self, ctx:frameQLParser.CurrentSchemaPriviLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#globalPrivLevel.
    def visitGlobalPrivLevel(self, ctx:frameQLParser.GlobalPrivLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#definiteSchemaPrivLevel.
    def visitDefiniteSchemaPrivLevel(self, ctx:frameQLParser.DefiniteSchemaPrivLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#definiteFullTablePrivLevel.
    def visitDefiniteFullTablePrivLevel(self, ctx:frameQLParser.DefiniteFullTablePrivLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#definiteTablePrivLevel.
    def visitDefiniteTablePrivLevel(self, ctx:frameQLParser.DefiniteTablePrivLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#renameUserClause.
    def visitRenameUserClause(self, ctx:frameQLParser.RenameUserClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#analyzeTable.
    def visitAnalyzeTable(self, ctx:frameQLParser.AnalyzeTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#checkTable.
    def visitCheckTable(self, ctx:frameQLParser.CheckTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#checksumTable.
    def visitChecksumTable(self, ctx:frameQLParser.ChecksumTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#optimizeTable.
    def visitOptimizeTable(self, ctx:frameQLParser.OptimizeTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#repairTable.
    def visitRepairTable(self, ctx:frameQLParser.RepairTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#checkTableOption.
    def visitCheckTableOption(self, ctx:frameQLParser.CheckTableOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#createUdfunction.
    def visitCreateUdfunction(self, ctx:frameQLParser.CreateUdfunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#installPlugin.
    def visitInstallPlugin(self, ctx:frameQLParser.InstallPluginContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uninstallPlugin.
    def visitUninstallPlugin(self, ctx:frameQLParser.UninstallPluginContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setVariable.
    def visitSetVariable(self, ctx:frameQLParser.SetVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setCharset.
    def visitSetCharset(self, ctx:frameQLParser.SetCharsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setNames.
    def visitSetNames(self, ctx:frameQLParser.SetNamesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setPassword.
    def visitSetPassword(self, ctx:frameQLParser.SetPasswordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setTransaction.
    def visitSetTransaction(self, ctx:frameQLParser.SetTransactionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#setAutocommit.
    def visitSetAutocommit(self, ctx:frameQLParser.SetAutocommitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showMasterLogs.
    def visitShowMasterLogs(self, ctx:frameQLParser.ShowMasterLogsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showLogEvents.
    def visitShowLogEvents(self, ctx:frameQLParser.ShowLogEventsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showObjectFilter.
    def visitShowObjectFilter(self, ctx:frameQLParser.ShowObjectFilterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showColumns.
    def visitShowColumns(self, ctx:frameQLParser.ShowColumnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showCreateDb.
    def visitShowCreateDb(self, ctx:frameQLParser.ShowCreateDbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showCreateFullIdObject.
    def visitShowCreateFullIdObject(self, ctx:frameQLParser.ShowCreateFullIdObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showCreateUser.
    def visitShowCreateUser(self, ctx:frameQLParser.ShowCreateUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showEngine.
    def visitShowEngine(self, ctx:frameQLParser.ShowEngineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showGlobalInfo.
    def visitShowGlobalInfo(self, ctx:frameQLParser.ShowGlobalInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showErrors.
    def visitShowErrors(self, ctx:frameQLParser.ShowErrorsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showCountErrors.
    def visitShowCountErrors(self, ctx:frameQLParser.ShowCountErrorsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showSchemaFilter.
    def visitShowSchemaFilter(self, ctx:frameQLParser.ShowSchemaFilterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showRoutine.
    def visitShowRoutine(self, ctx:frameQLParser.ShowRoutineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showGrants.
    def visitShowGrants(self, ctx:frameQLParser.ShowGrantsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showIndexes.
    def visitShowIndexes(self, ctx:frameQLParser.ShowIndexesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showOpenTables.
    def visitShowOpenTables(self, ctx:frameQLParser.ShowOpenTablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showProfile.
    def visitShowProfile(self, ctx:frameQLParser.ShowProfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showSlaveStatus.
    def visitShowSlaveStatus(self, ctx:frameQLParser.ShowSlaveStatusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#variableClause.
    def visitVariableClause(self, ctx:frameQLParser.VariableClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showCommonEntity.
    def visitShowCommonEntity(self, ctx:frameQLParser.ShowCommonEntityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showFilter.
    def visitShowFilter(self, ctx:frameQLParser.ShowFilterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showGlobalInfoClause.
    def visitShowGlobalInfoClause(self, ctx:frameQLParser.ShowGlobalInfoClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showSchemaEntity.
    def visitShowSchemaEntity(self, ctx:frameQLParser.ShowSchemaEntityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#showProfileType.
    def visitShowProfileType(self, ctx:frameQLParser.ShowProfileTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#binlogStatement.
    def visitBinlogStatement(self, ctx:frameQLParser.BinlogStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#cacheIndexStatement.
    def visitCacheIndexStatement(self, ctx:frameQLParser.CacheIndexStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#flushStatement.
    def visitFlushStatement(self, ctx:frameQLParser.FlushStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#killStatement.
    def visitKillStatement(self, ctx:frameQLParser.KillStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#loadIndexIntoCache.
    def visitLoadIndexIntoCache(self, ctx:frameQLParser.LoadIndexIntoCacheContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#resetStatement.
    def visitResetStatement(self, ctx:frameQLParser.ResetStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#shutdownStatement.
    def visitShutdownStatement(self, ctx:frameQLParser.ShutdownStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableIndexes.
    def visitTableIndexes(self, ctx:frameQLParser.TableIndexesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleFlushOption.
    def visitSimpleFlushOption(self, ctx:frameQLParser.SimpleFlushOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#channelFlushOption.
    def visitChannelFlushOption(self, ctx:frameQLParser.ChannelFlushOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableFlushOption.
    def visitTableFlushOption(self, ctx:frameQLParser.TableFlushOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#flushTableOption.
    def visitFlushTableOption(self, ctx:frameQLParser.FlushTableOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#loadedTableIndexes.
    def visitLoadedTableIndexes(self, ctx:frameQLParser.LoadedTableIndexesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleDescribeStatement.
    def visitSimpleDescribeStatement(self, ctx:frameQLParser.SimpleDescribeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#fullDescribeStatement.
    def visitFullDescribeStatement(self, ctx:frameQLParser.FullDescribeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#helpStatement.
    def visitHelpStatement(self, ctx:frameQLParser.HelpStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#useStatement.
    def visitUseStatement(self, ctx:frameQLParser.UseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#describeStatements.
    def visitDescribeStatements(self, ctx:frameQLParser.DescribeStatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#describeConnection.
    def visitDescribeConnection(self, ctx:frameQLParser.DescribeConnectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#fullId.
    def visitFullId(self, ctx:frameQLParser.FullIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tableName.
    def visitTableName(self, ctx:frameQLParser.TableNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#fullColumnName.
    def visitFullColumnName(self, ctx:frameQLParser.FullColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexColumnName.
    def visitIndexColumnName(self, ctx:frameQLParser.IndexColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userName.
    def visitUserName(self, ctx:frameQLParser.UserNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#mysqlVariable.
    def visitMysqlVariable(self, ctx:frameQLParser.MysqlVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#charsetName.
    def visitCharsetName(self, ctx:frameQLParser.CharsetNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#collationName.
    def visitCollationName(self, ctx:frameQLParser.CollationNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#engineName.
    def visitEngineName(self, ctx:frameQLParser.EngineNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uuidSet.
    def visitUuidSet(self, ctx:frameQLParser.UuidSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xid.
    def visitXid(self, ctx:frameQLParser.XidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#xuidStringId.
    def visitXuidStringId(self, ctx:frameQLParser.XuidStringIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#authPlugin.
    def visitAuthPlugin(self, ctx:frameQLParser.AuthPluginContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uid.
    def visitUid(self, ctx:frameQLParser.UidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleId.
    def visitSimpleId(self, ctx:frameQLParser.SimpleIdContext):
        #todo handle children, right now assuming TupleValueExpr
        return TupleValueExpression(ctx.getText())
        # return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dottedId.
    def visitDottedId(self, ctx:frameQLParser.DottedIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#decimalLiteral.
    def visitDecimalLiteral(self, ctx:frameQLParser.DecimalLiteralContext):
        return ConstantValueExpression(int(ctx.getText()))
        

    # Visit a parse tree produced by frameQLParser#fileSizeLiteral.
    def visitFileSizeLiteral(self, ctx:frameQLParser.FileSizeLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stringLiteral.
    def visitStringLiteral(self, ctx:frameQLParser.StringLiteralContext):
        if ctx.STRING_LITERAL() is not None:
            return ConstantValueExpression(ctx.getText())
        #todo handle other types    
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#booleanLiteral.
    def visitBooleanLiteral(self, ctx:frameQLParser.BooleanLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#hexadecimalLiteral.
    def visitHexadecimalLiteral(self, ctx:frameQLParser.HexadecimalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#nullNotnull.
    def visitNullNotnull(self, ctx:frameQLParser.NullNotnullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#constant.
    def visitConstant(self, ctx:frameQLParser.ConstantContext):
        if ctx.REAL_LITERAL() is not None:
             return ConstantValueExpression(float(ctx.getText()))
        
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#stringDataType.
    def visitStringDataType(self, ctx:frameQLParser.StringDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dimensionDataType.
    def visitDimensionDataType(self, ctx:frameQLParser.DimensionDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleDataType.
    def visitSimpleDataType(self, ctx:frameQLParser.SimpleDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#collectionDataType.
    def visitCollectionDataType(self, ctx:frameQLParser.CollectionDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#spatialDataType.
    def visitSpatialDataType(self, ctx:frameQLParser.SpatialDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#convertedDataType.
    def visitConvertedDataType(self, ctx:frameQLParser.ConvertedDataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lengthOneDimension.
    def visitLengthOneDimension(self, ctx:frameQLParser.LengthOneDimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lengthTwoDimension.
    def visitLengthTwoDimension(self, ctx:frameQLParser.LengthTwoDimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#lengthTwoOptionalDimension.
    def visitLengthTwoOptionalDimension(self, ctx:frameQLParser.LengthTwoOptionalDimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#uidList.
    def visitUidList(self, ctx:frameQLParser.UidListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#tables.
    def visitTables(self, ctx:frameQLParser.TablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#indexColumnNames.
    def visitIndexColumnNames(self, ctx:frameQLParser.IndexColumnNamesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#expressions.
    def visitExpressions(self, ctx:frameQLParser.ExpressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#expressionsWithDefaults.
    def visitExpressionsWithDefaults(self, ctx:frameQLParser.ExpressionsWithDefaultsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#constants.
    def visitConstants(self, ctx:frameQLParser.ConstantsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleStrings.
    def visitSimpleStrings(self, ctx:frameQLParser.SimpleStringsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#userVariables.
    def visitUserVariables(self, ctx:frameQLParser.UserVariablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#defaultValue.
    def visitDefaultValue(self, ctx:frameQLParser.DefaultValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#currentTimestamp.
    def visitCurrentTimestamp(self, ctx:frameQLParser.CurrentTimestampContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#expressionOrDefault.
    def visitExpressionOrDefault(self, ctx:frameQLParser.ExpressionOrDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ifExists.
    def visitIfExists(self, ctx:frameQLParser.IfExistsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#ifNotExists.
    def visitIfNotExists(self, ctx:frameQLParser.IfNotExistsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#specificFunctionCall.
    def visitSpecificFunctionCall(self, ctx:frameQLParser.SpecificFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#aggregateFunctionCall.
    def visitAggregateFunctionCall(self, ctx:frameQLParser.AggregateFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#scalarFunctionCall.
    def visitScalarFunctionCall(self, ctx:frameQLParser.ScalarFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#udfFunctionCall.
    def visitUdfFunctionCall(self, ctx:frameQLParser.UdfFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#passwordFunctionCall.
    def visitPasswordFunctionCall(self, ctx:frameQLParser.PasswordFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#simpleFunctionCall.
    def visitSimpleFunctionCall(self, ctx:frameQLParser.SimpleFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dataTypeFunctionCall.
    def visitDataTypeFunctionCall(self, ctx:frameQLParser.DataTypeFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#valuesFunctionCall.
    def visitValuesFunctionCall(self, ctx:frameQLParser.ValuesFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#caseFunctionCall.
    def visitCaseFunctionCall(self, ctx:frameQLParser.CaseFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#charFunctionCall.
    def visitCharFunctionCall(self, ctx:frameQLParser.CharFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#positionFunctionCall.
    def visitPositionFunctionCall(self, ctx:frameQLParser.PositionFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#substrFunctionCall.
    def visitSubstrFunctionCall(self, ctx:frameQLParser.SubstrFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#trimFunctionCall.
    def visitTrimFunctionCall(self, ctx:frameQLParser.TrimFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#weightFunctionCall.
    def visitWeightFunctionCall(self, ctx:frameQLParser.WeightFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#extractFunctionCall.
    def visitExtractFunctionCall(self, ctx:frameQLParser.ExtractFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#getFormatFunctionCall.
    def visitGetFormatFunctionCall(self, ctx:frameQLParser.GetFormatFunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#caseFuncAlternative.
    def visitCaseFuncAlternative(self, ctx:frameQLParser.CaseFuncAlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#levelWeightList.
    def visitLevelWeightList(self, ctx:frameQLParser.LevelWeightListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#levelWeightRange.
    def visitLevelWeightRange(self, ctx:frameQLParser.LevelWeightRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#levelInWeightListElement.
    def visitLevelInWeightListElement(self, ctx:frameQLParser.LevelInWeightListElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#aggregateWindowedFunction.
    def visitAggregateWindowedFunction(self, ctx:frameQLParser.AggregateWindowedFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#scalarFunctionName.
    def visitScalarFunctionName(self, ctx:frameQLParser.ScalarFunctionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#passwordFunctionClause.
    def visitPasswordFunctionClause(self, ctx:frameQLParser.PasswordFunctionClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#functionArgs.
    def visitFunctionArgs(self, ctx:frameQLParser.FunctionArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#functionArg.
    def visitFunctionArg(self, ctx:frameQLParser.FunctionArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#isExpression.
    def visitIsExpression(self, ctx:frameQLParser.IsExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#notExpression.
    def visitNotExpression(self, ctx:frameQLParser.NotExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#logicalExpression.
    def visitLogicalExpression(self, ctx:frameQLParser.LogicalExpressionContext):
        if len(ctx.children) < 3:
            #error scenario, should have 3 children
            return None
        left =  self.visit(ctx.getChild(0))
        op   =  self.visit(ctx.getChild(1))
        right=  self.visit(ctx.getChild(2))        
        return LogicalExpression(op, left, right)


    # Visit a parse tree produced by frameQLParser#predicateExpression.
    def visitPredicateExpression(self, ctx:frameQLParser.PredicateExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#soundsLikePredicate.
    def visitSoundsLikePredicate(self, ctx:frameQLParser.SoundsLikePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#expressionAtomPredicate.
    def visitExpressionAtomPredicate(self, ctx:frameQLParser.ExpressionAtomPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#inPredicate.
    def visitInPredicate(self, ctx:frameQLParser.InPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subqueryComparasionPredicate.
    def visitSubqueryComparasionPredicate(self, ctx:frameQLParser.SubqueryComparasionPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#betweenPredicate.
    def visitBetweenPredicate(self, ctx:frameQLParser.BetweenPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#binaryComparasionPredicate.
    def visitBinaryComparasionPredicate(self, ctx:frameQLParser.BinaryComparasionPredicateContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op   = self.visit(ctx.comparisonOperator())
        return ComparisonExpression(op, left, right)
       

    # Visit a parse tree produced by frameQLParser#isNullPredicate.
    def visitIsNullPredicate(self, ctx:frameQLParser.IsNullPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#likePredicate.
    def visitLikePredicate(self, ctx:frameQLParser.LikePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#regexpPredicate.
    def visitRegexpPredicate(self, ctx:frameQLParser.RegexpPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unaryExpressionAtom.
    def visitUnaryExpressionAtom(self, ctx:frameQLParser.UnaryExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#collateExpressionAtom.
    def visitCollateExpressionAtom(self, ctx:frameQLParser.CollateExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#subqueryExpessionAtom.
    def visitSubqueryExpessionAtom(self, ctx:frameQLParser.SubqueryExpessionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#mysqlVariableExpressionAtom.
    def visitMysqlVariableExpressionAtom(self, ctx:frameQLParser.MysqlVariableExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#nestedExpressionAtom.
    def visitNestedExpressionAtom(self, ctx:frameQLParser.NestedExpressionAtomContext):
        #ToDo Can there be >1 expression in this case
        expr = ctx.expression(0)
        return self.visit(expr)


    # Visit a parse tree produced by frameQLParser#nestedRowExpressionAtom.
    def visitNestedRowExpressionAtom(self, ctx:frameQLParser.NestedRowExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#mathExpressionAtom.
    def visitMathExpressionAtom(self, ctx:frameQLParser.MathExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#intervalExpressionAtom.
    def visitIntervalExpressionAtom(self, ctx:frameQLParser.IntervalExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#existsExpessionAtom.
    def visitExistsExpessionAtom(self, ctx:frameQLParser.ExistsExpessionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#constantExpressionAtom.
    def visitConstantExpressionAtom(self, ctx:frameQLParser.ConstantExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#functionCallExpressionAtom.
    def visitFunctionCallExpressionAtom(self, ctx:frameQLParser.FunctionCallExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#binaryExpressionAtom.
    def visitBinaryExpressionAtom(self, ctx:frameQLParser.BinaryExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#fullColumnNameExpressionAtom.
    def visitFullColumnNameExpressionAtom(self, ctx:frameQLParser.FullColumnNameExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#bitExpressionAtom.
    def visitBitExpressionAtom(self, ctx:frameQLParser.BitExpressionAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#unaryOperator.
    def visitUnaryOperator(self, ctx:frameQLParser.UnaryOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx:frameQLParser.ComparisonOperatorContext):
        op = ctx.getText()
        if op == '=':
            return ExpressionType.COMPARE_EQUAL
        elif op == '<':
            return ExpressionType.COMPARE_LESSER
        elif op == '>':
            return ExpressionType.COMPARE_GREATER
        else:
            return ExpressionType.INVALID
        

    # Visit a parse tree produced by frameQLParser#logicalOperator.
    def visitLogicalOperator(self, ctx:frameQLParser.LogicalOperatorContext):
        op = ctx.getText()
        
        if op == 'OR':
            return ExpressionType.LOGICAL_OR
        elif op == 'AND':
            return ExpressionType.LOGICAL_AND
        else:
            return ExpressionType.INVALID
        


    # Visit a parse tree produced by frameQLParser#bitOperator.
    def visitBitOperator(self, ctx:frameQLParser.BitOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#mathOperator.
    def visitMathOperator(self, ctx:frameQLParser.MathOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#charsetNameBase.
    def visitCharsetNameBase(self, ctx:frameQLParser.CharsetNameBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#transactionLevelBase.
    def visitTransactionLevelBase(self, ctx:frameQLParser.TransactionLevelBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#privilegesBase.
    def visitPrivilegesBase(self, ctx:frameQLParser.PrivilegesBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#intervalTypeBase.
    def visitIntervalTypeBase(self, ctx:frameQLParser.IntervalTypeBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#dataTypeBase.
    def visitDataTypeBase(self, ctx:frameQLParser.DataTypeBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#keywordsCanBeId.
    def visitKeywordsCanBeId(self, ctx:frameQLParser.KeywordsCanBeIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by frameQLParser#functionNameBase.
    def visitFunctionNameBase(self, ctx:frameQLParser.FunctionNameBaseContext):
        return self.visitChildren(ctx)



