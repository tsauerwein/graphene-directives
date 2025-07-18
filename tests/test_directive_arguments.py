from pathlib import Path

import graphene
import pytest
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    directive,
    build_schema,
)
from graphene_directives.exceptions import DirectiveInvalidArgValueTypeError

curr_dir = Path(__file__).parent

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
    is_repeatable=True,
)

DbCacheDirective = CustomDirective(
    name="db_cache",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
            default_value=12,
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
)


class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = graphene.Int(required=True)


class QueryWithDirective(graphene.ObjectType):
    position = directive(CacheDirective, field=graphene.Field(Position), max_age=300)

    question = graphene.Field(
        graphene.String, form_id=graphene.Int(required=True), description="A question"
    )

    score = graphene.Field(
        graphene.Int, form_id=graphene.Int(required=True), description="A score"
    )


schema_with_directive = build_schema(
    query=QueryWithDirective, directives=(CacheDirective,)
)


def test_input_argument_on_class() -> None:
    with pytest.raises(Exception) as e_info:

        @directive(target_directive=CacheDirective, required=True)
        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)

    assert e_info.type == DirectiveInvalidArgValueTypeError


def test_input_argument_on_field() -> None:
    with pytest.raises(Exception) as e_info:

        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=CacheDirective,
                field=graphene.Int(
                    required=True,
                    deprecation_reason="This field is deprecated and will be removed in future",
                ),
            )

    assert e_info.type == DirectiveInvalidArgValueTypeError


def test_input_default_argument_on_class() -> None:
    @directive(target_directive=DbCacheDirective, required=True)
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)


def test_input_default_argument_on_field() -> None:
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)
        kind = directive(
            target_directive=DbCacheDirective,
            field=graphene.Int(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
        )


def test_generate_schema_with_arguments() -> None:
    """Test that argument names are converted to camel-case."""
    with open(
        f"{curr_dir}/schema_files/test_directive_arguments_camel_case.graphql"
    ) as f:
        assert str(schema_with_directive) == f.read()
