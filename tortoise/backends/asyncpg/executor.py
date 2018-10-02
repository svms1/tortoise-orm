from pypika import Table

from tortoise.backends.base.executor import BaseExecutor


class AsyncpgExecutor(BaseExecutor):
    async def execute_insert(self, instance):
        self.connection = await self.db.get_single_connection()
        regular_columns, columns = self._prepare_insert_columns()
        values = self._prepare_insert_values(
            instance=instance,
            regular_columns=regular_columns,
        )

        query = str(
            self.connection.query_class.into(Table(self.model._meta.table)).columns(*columns)
            .insert(*values).returning('id')
        )
        result = await self.connection.execute_query(query)
        instance.id = result[0][0]
        await self.db.release_single_connection(self.connection)
        self.connection = None
        return instance
