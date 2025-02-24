# coding=utf-8
# Copyright 2024 HuggingFace Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from smolagents import DuckDuckGoSearchTool

from .test_tools import ToolTesterMixin
from .utils.markers import require_run_all


class DuckDuckGoSearchToolTester(unittest.TestCase, ToolTesterMixin):
    def setUp(self):
        self.tool = DuckDuckGoSearchTool()
        self.tool.setup()

    @require_run_all
    def test_exact_match_arg(self):
        result = self.tool("Agents")
        assert isinstance(result, str)
