/*
 * Copyright (c) 2026 PCL-CCNN
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package tools

import (
	"context"

	"github.com/google/jsonschema-go/jsonschema"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func AddToolsToServer(server *mcp.Server) {
	for _, addToolFunc := range toolsToAdd {
		addToolFunc(server)
	}
}

var toolsToAdd []func(server *mcp.Server)

func registerTool[I, O any](tool MCPTool[I, O]) {
	t := &mcp.Tool{
		Name: tool.Name, Description: tool.Description,
	}
	if tool.In != nil {
		t.InputSchema = tool.In
	}
	if tool.Out != nil {
		t.OutputSchema = tool.Out
	}
	toolsToAdd = append(toolsToAdd, func(server *mcp.Server) {
		mcp.AddTool(server, t, tool.Handler)
	})
}

type MCPTool[I, O any] struct {
	Name        string
	Description string
	In          *jsonschema.Schema
	Out         *jsonschema.Schema
	Handler     func(ctx context.Context, request *mcp.CallToolRequest, in I) (*mcp.CallToolResult, O, error)
}
