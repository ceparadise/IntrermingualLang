package org.apache.maven.plugin.pom;

/*
 * Copyright 2001-2004 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.maven.artifact.Artifact;
import org.apache.maven.artifact.DefaultArtifact;
import org.apache.maven.artifact.deployer.ArtifactDeployer;
import org.apache.maven.artifact.repository.ArtifactRepository;
import org.apache.maven.artifact.repository.ArtifactRepositoryFactory;
import org.apache.maven.model.Repository;
import org.apache.maven.plugin.AbstractPlugin;
import org.apache.maven.plugin.PluginExecutionRequest;
import org.apache.maven.plugin.PluginExecutionResponse;
import org.apache.maven.project.MavenProject;
import org.apache.maven.settings.MavenSettings;

import java.io.File;

/**
 * @goal deploy
 * @description deploys a pom to remote repository
 * @parameter name="deployer"
 *  type="org.apache.maven.artifact.deployer.ArtifactDeployer"
 *  required="true" 
 *  validator=""
 *  expression="#component.org.apache.maven.artifact.deployer.ArtifactDeployer"
 *  description=""
 * @parameter name="project"
 *  type="org.apache.maven.project.MavenProject"
 *  required="true"
 *  validator=""
 *  expression="#project"
 *  description=""
 * @parameter name="deployer"
 *  type="org.apache.maven.artifact.deployer.ArtifactDeployer"
 *  required="true"
 *  validator=""
 *  expression="#component.org.apache.maven.artifact.deployer.ArtifactDeployer"
 *  description=""
 * @parameter
 *  name="deploymentRepository"
 *  type="org.apache.maven.artifact.repository.ArtifactRepository"
 *  required="true"
 *  validator=""
 *  expression="#project.distributionManagementArtifactRepository"
 *  description=""
 */
public class PomDeployMojo
    extends AbstractPlugin
{
    public void execute( PluginExecutionRequest request, PluginExecutionResponse response ) throws Exception
    {
        MavenProject project = (MavenProject) request.getParameter( "project" );

        ArtifactDeployer artifactDeployer = (ArtifactDeployer) request.getParameter( "deployer" );

        ArtifactRepository deploymentRepository = (ArtifactRepository) request.getParameter( "deploymentRepository" );

        if ( deploymentRepository == null )
        {
            String msg = "Deployment failed: repository element" + " was not specified in the pom inside"
                + " distributionManagement element";
            throw new Exception( msg );
        }

        if ( deploymentRepository.getAuthenticationInfo() == null )
        {
            getLog().warn(
                           "Deployment repository {id: \'" + deploymentRepository.getId()
                               + "\'} has no associated authentication info!" );
        }

        Artifact artifact = new DefaultArtifact( project.getGroupId(), project.getArtifactId(), project.getVersion(),
                                                 "pom" );

        File pom = new File( project.getFile().getParentFile(), "pom.xml" );

        artifactDeployer.deploy( pom, artifact, deploymentRepository );
    }
}