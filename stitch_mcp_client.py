#!/usr/bin/env python3

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import requests


DEFAULT_URL = "https://stitch.googleapis.com/mcp"
DEFAULT_PROTOCOL_VERSION = "2025-03-26"
DEFAULT_TIMEOUT_SECONDS = 30


class McpError(RuntimeError):
    pass


@dataclass
class JsonRpcResponse:
    payload: Dict[str, Any]
    headers: requests.structures.CaseInsensitiveDict[str]


class StitchMcpClient:
    def __init__(
        self,
        url: str,
        api_key: str,
        protocol_version: str = DEFAULT_PROTOCOL_VERSION,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.protocol_version = protocol_version
        self.timeout_seconds = timeout_seconds
        self.session_id: Optional[str] = None
        self._next_id = 1
        self._http = requests.Session()
        self._base_headers = {
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "math-app-stitch-client/0.1.0",
        }

    def initialize(self) -> Dict[str, Any]:
        response = self._post_request(
            method="initialize",
            params={
                "protocolVersion": self.protocol_version,
                "capabilities": {},
                "clientInfo": {
                    "name": "math-app-stitch-client",
                    "version": "0.1.0",
                },
            },
            include_protocol_header=False,
            include_session_header=False,
        )
        result = response["result"]
        self.protocol_version = result.get("protocolVersion", self.protocol_version)
        return result

    def initialized(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        response = self._http.post(
            self.url,
            headers=self._request_headers(),
            json=payload,
            timeout=self.timeout_seconds,
        )
        if response.status_code != 202:
            self._raise_http_error(response, "initialized notification failed")

    def list_tools(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if cursor:
            params["cursor"] = cursor
        response = self._post_request(method="tools/list", params=params)
        return response["result"]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        response = self._post_request(
            method="tools/call",
            params={"name": name, "arguments": arguments},
        )
        return response["result"]

    def close(self) -> None:
        headers = self._request_headers()
        if self.session_id:
            delete_response = self._http.delete(
                self.url,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            if delete_response.status_code not in (200, 202, 204, 405):
                self._raise_http_error(delete_response, "session close failed")
        self._http.close()

    def _post_request(
        self,
        method: str,
        params: Dict[str, Any],
        *,
        include_protocol_header: bool = True,
        include_session_header: bool = True,
        retry_on_session_expiry: bool = True,
    ) -> Dict[str, Any]:
        request_id = self._take_request_id()
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        headers = self._request_headers(
            include_protocol_header=include_protocol_header,
            include_session_header=include_session_header,
        )

        response = self._http.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=self.timeout_seconds,
            stream=True,
        )

        if response.status_code == 404 and self.session_id and retry_on_session_expiry:
            self.session_id = None
            self.initialize()
            self.initialized()
            return self._post_request(
                method,
                params,
                include_protocol_header=True,
                include_session_header=True,
                retry_on_session_expiry=False,
            )

        if response.status_code >= 400:
            self._raise_http_error(response, f"request failed for {method}")

        parsed = self._parse_rpc_response(response, request_id)
        session_id = parsed.headers.get("Mcp-Session-Id")
        if session_id:
            self.session_id = session_id
        self._validate_jsonrpc_response(parsed.payload, request_id, method)
        return parsed.payload

    def _parse_rpc_response(self, response: requests.Response, request_id: int) -> JsonRpcResponse:
        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            payload = self._parse_sse_response(response, request_id)
        else:
            try:
                payload = response.json()
            except json.JSONDecodeError as exc:
                raise McpError(f"invalid JSON response: {exc}") from exc
        return JsonRpcResponse(payload=payload, headers=response.headers)

    def _parse_sse_response(self, response: requests.Response, request_id: int) -> Dict[str, Any]:
        event_type: Optional[str] = None
        data_lines = []

        for raw_line in response.iter_lines(decode_unicode=True):
            if raw_line is None:
                continue
            line = raw_line.strip("\r")
            if not line:
                if not data_lines:
                    event_type = None
                    continue
                payload = json.loads("\n".join(data_lines))
                if self._matches_request_id(payload, request_id):
                    return payload
                event_type = None
                data_lines = []
                continue
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                event_type = line.partition(":")[2].strip()
                continue
            if line.startswith("data:"):
                data_lines.append(line.partition(":")[2].lstrip())
                continue
            if event_type == "message":
                data_lines.append(line)

        raise McpError(f"SSE stream ended before response for request id {request_id}")

    def _request_headers(
        self,
        *,
        include_protocol_header: bool = True,
        include_session_header: bool = True,
    ) -> Dict[str, str]:
        headers = dict(self._base_headers)
        if include_protocol_header:
            headers["MCP-Protocol-Version"] = self.protocol_version
        if include_session_header and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    def _take_request_id(self) -> int:
        request_id = self._next_id
        self._next_id += 1
        return request_id

    @staticmethod
    def _matches_request_id(payload: Any, request_id: int) -> bool:
        if isinstance(payload, list):
            return any(item.get("id") == request_id for item in payload if isinstance(item, dict))
        return isinstance(payload, dict) and payload.get("id") == request_id

    @staticmethod
    def _validate_jsonrpc_response(payload: Any, request_id: int, method: str) -> None:
        if isinstance(payload, list):
            matches = [item for item in payload if isinstance(item, dict) and item.get("id") == request_id]
            if not matches:
                raise McpError(f"no JSON-RPC response found for request id {request_id}")
            payload = matches[0]
        if not isinstance(payload, dict):
            raise McpError(f"unexpected JSON-RPC payload type for {method}: {type(payload).__name__}")
        if payload.get("jsonrpc") != "2.0":
            raise McpError(f"invalid JSON-RPC version in response for {method}")
        if payload.get("id") != request_id:
            raise McpError(f"unexpected response id for {method}: {payload.get('id')}")
        if "error" in payload:
            error = payload["error"]
            code = error.get("code")
            message = error.get("message")
            raise McpError(f"JSON-RPC error for {method}: {code} {message}")
        if "result" not in payload:
            raise McpError(f"missing result in response for {method}")

    @staticmethod
    def _raise_http_error(response: requests.Response, prefix: str) -> None:
        body = response.text.strip()
        snippet = body[:500] if body else "<empty body>"
        raise McpError(f"{prefix}: HTTP {response.status_code}: {snippet}")


def format_tools(tools: Iterable[Dict[str, Any]]) -> str:
    lines = []
    for tool in tools:
        description = tool.get("description") or ""
        lines.append(f"- {tool['name']}: {description}")
        input_schema = tool.get("inputSchema")
        if input_schema:
            lines.append(json.dumps(input_schema, indent=2, sort_keys=True))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone Stitch MCP client")
    parser.add_argument("command", choices=["list-tools", "call-tool"], help="MCP operation to run")
    parser.add_argument("--tool", help="Tool name for call-tool")
    parser.add_argument(
        "--arguments",
        default="{}",
        help="JSON object for tool arguments when using call-tool",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("STITCH_MCP_URL", DEFAULT_URL),
        help="Stitch MCP endpoint URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("STITCH_API_KEY") or os.environ.get("X_GOOG_API_KEY"),
        help="Stitch API key. Defaults to STITCH_API_KEY or X_GOOG_API_KEY",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Request timeout in seconds",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing API key. Pass --api-key or set STITCH_API_KEY.", file=sys.stderr)
        return 2
    try:
        tool_args = json.loads(args.arguments)
    except json.JSONDecodeError as exc:
        print(f"Invalid --arguments JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(tool_args, dict):
        print("--arguments must decode to a JSON object.", file=sys.stderr)
        return 2
    if args.command == "call-tool" and not args.tool:
        print("--tool is required for call-tool.", file=sys.stderr)
        return 2

    client = StitchMcpClient(
        url=args.url,
        api_key=args.api_key,
        timeout_seconds=args.timeout,
    )
    try:
        initialize_result = client.initialize()
        client.initialized()

        print("Initialized MCP session")
        print(json.dumps(initialize_result, indent=2, sort_keys=True))

        if args.command == "list-tools":
            tools_result = client.list_tools()
            tools = tools_result.get("tools", [])
            print(f"\nDiscovered {len(tools)} tools")
            print(format_tools(tools))
        else:
            call_result = client.call_tool(args.tool, tool_args)
            print(json.dumps(call_result, indent=2, sort_keys=True))
    except (McpError, requests.RequestException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())