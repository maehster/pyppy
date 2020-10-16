from argparse import ArgumentParser, Namespace

from pyppy.conditions.conditions import condition, s_, and_, or_
from test.utils.testcase import TestCase
from pyppy.config.get_config import initialize_config, destroy_config, config


class ConditionsTest(TestCase):

    def setUp(self) -> None:
        destroy_config()

    def test_single_condition_true(self):
        parser = ArgumentParser()
        parser.add_argument("--tmp1", type=int)

        cli_args = ["--tmp1", "1"]

        args = parser.parse_args(cli_args)

        initialize_config(args)

        @condition(s_(lambda c: c.tmp1 == 1))
        def tmp():
            return "returned"

        self.assertTrue(tmp() == "returned")

    def test_single_condition_false(self):
        parser = ArgumentParser()
        parser.add_argument("--tmp1", type=int)

        cli_args = ["--tmp1", "1"]

        args = parser.parse_args(cli_args)

        initialize_config(args)

        @condition(s_(lambda c: c.tmp1 == 2))
        def tmp():
            return "returned"

        self.assertIsNone(tmp())

    def test_initialize_after(self):
        """
        Test if initialization works after defining
        a method with a condition.
        """

        parser = ArgumentParser()
        parser.add_argument("--tmp1", type=int)

        cli_args = ["--tmp1", "1"]

        args = parser.parse_args(cli_args)

        @condition(s_(lambda c: c.tmp1 == 1))
        def tmp():
            return "returned"

        initialize_config(args)

        self.assertEqual(tmp(), "returned")

    def test_subparser_condition(self):
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")

        parser_sub1 = subparsers.add_parser('sub1')
        parser_sub1.add_argument('--sub1-tmp', type=int)

        parser_sub2 = subparsers.add_parser('sub2')
        parser_sub2.add_argument('--sub2-tmp', type=int)

        args = parser.parse_args(["sub1", "--sub1-tmp", "1"])
        initialize_config(args)
        self.assertEqual(config().sub1_tmp, 1)

        # raise when sub command check comes second
        @condition(
            and_(
                s_(lambda c: c.sub2_tmp == 2),
                s_(lambda c: c.command == "sub2")
            )
        )
        def tmp1():
            return "returned"

        with self.assertRaises(AttributeError):
            tmp1()

        # don't raise when sub command check comes first
        @condition(
            and_(
                s_(lambda c: c.command == "sub2"),
                s_(lambda c: c.sub2_tmp == 2)
            )
        )
        def tmp2():
            return "returned"

        with self.assertNotRaises(AttributeError):
            tmp2()

        self.assertIsNone(tmp2())

        # return
        @condition(
            and_(
                s_(lambda c: c.command == "sub1"),
                s_(lambda c: c.sub1_tmp == 1)
            )
        )
        def tmp3():
            return "returned"

        self.assertEqual(tmp3(), "returned")

    def test_single_exp(self):
        @condition(s_(a="b"))
        def tmp():
            return "returned"

        initialize_config(Namespace())
        conf = config()
        conf._allow_overriding = True
        conf.a = "b"
        self.assertTrue(tmp() == "returned")

        conf.a = "c"
        self.assertIsNone(tmp())

    def test_nested_exp_1(self):
        exp = and_(
            or_(
                s_(a="b"),
                s_(b="c")
            ),
            s_(d="e")
        )

        @condition(exp)
        def tmp():
            return "returned"

        initialize_config(Namespace())
        conf = config()
        conf.a = "b"
        conf.d = "e"
        self.assertTrue(tmp() == "returned")

    def test_nested_exp_2(self):
        exp = and_(
            or_(
                s_(a="b"),
                s_(b="c")
            ),
            s_(d="e")
        )

        @condition(exp)
        def tmp():
            return "returned"

        initialize_config(Namespace())
        conf = config()
        conf.b = "c"
        conf.d = "e"
        self.assertTrue(tmp() == "returned")

    def test_nested_exp_3(self):
        exp = and_(
            or_(
                s_(a="b"),
                s_(b="c")
            ),
            s_(d="e")
        )

        @condition(exp)
        def tmp():
            return "returned"

        initialize_config(Namespace())
        conf = config()
        conf.a = "b"
        conf.b = "c"

        self.assertIsNone(tmp())

    def test_nested_exp_4(self):
        exp = and_(
            or_(
                s_(a="b"),
                s_(b="c")
            ),
            s_(d="e")
        )

        @condition(exp)
        def tmp():
            return "returned"

        initialize_config(Namespace())
        conf = config()
        conf.d = "e"

        self.assertIsNone(tmp())

    def test_expressions(self):
        initialize_config(Namespace())
        conf = config()
        conf.a = "b"

        exp = or_(
            s_(a="b"),
            s_(b="c")
        )

        self.assertTrue(exp())

        delattr(conf, "a")
        self.assertFalse(exp())