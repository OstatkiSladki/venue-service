from __future__ import annotations

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from src.config import get_settings
from src.grpc.generated import venue_directory_pb2_grpc
from src.grpc.service import VenueDirectoryGrpcService

_SERVICE_NAME = "ostatki.grpc.v1.VenueDirectoryService"


async def start_grpc_server() -> tuple[grpc.aio.Server, health.HealthServicer]:
  settings = get_settings()
  server = grpc.aio.server()
  health_servicer = health.aio.HealthServicer()

  venue_directory_pb2_grpc.add_VenueDirectoryServiceServicer_to_server(
    VenueDirectoryGrpcService(),
    server,
  )
  health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

  server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
  await server.start()

  await health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
  await health_servicer.set(_SERVICE_NAME, health_pb2.HealthCheckResponse.SERVING)
  return server, health_servicer


async def stop_grpc_server(
  server: grpc.aio.Server,
  health_servicer: health.HealthServicer,
) -> None:
  await health_servicer.set(_SERVICE_NAME, health_pb2.HealthCheckResponse.NOT_SERVING)
  await health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
  await server.stop(grace=5)
