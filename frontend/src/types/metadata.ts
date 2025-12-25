/**
 * TypeScript types for database metadata.
 */

export interface Schema {
  name: string;
}

export interface Table {
  name: string;
  schema: string;
  table_type: string;
}

export interface Column {
  name: string;
  data_type: string;
  is_nullable: boolean;
  column_default?: string | null;
}

export interface ForeignKey {
  column_name: string;
  referenced_table: string;
  referenced_column: string;
}

export interface TableDetails {
  name: string;
  schema: string;
  row_count?: number | null;
  columns: Column[];
  foreign_keys: ForeignKey[];
}

export interface MetadataRefreshResponse {
  success: boolean;
  message: string;
}
