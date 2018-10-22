package org.apache.maven.project.injection;

/*
 * Copyright 2001-2005 The Apache Software Foundation.
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

import org.apache.maven.model.Dependency;
import org.apache.maven.model.DependencyManagement;
import org.apache.maven.model.Goal;
import org.apache.maven.model.Model;
import org.apache.maven.model.Plugin;
import org.apache.maven.model.PluginManagement;
import org.codehaus.plexus.util.xml.Xpp3Dom;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * @author jdcasey Created on Feb 1, 2005
 */
public class DefaultModelDefaultsInjector
    implements ModelDefaultsInjector
{

    public void injectDefaults( Model model )
    {
        injectDependencyDefaults( model.getDependencies(), model.getDependencyManagement() );
        if ( model.getBuild() != null )
        {
            injectPluginDefaults( model.getBuild().getPlugins(), model.getBuild().getPluginManagement() );
        }
    }

    private void injectPluginDefaults( List plugins, PluginManagement pluginManagement )
    {
        if ( pluginManagement != null )
        {
            // a given project's plugins should be smaller than the
            // group-defined defaults set...
            // in other words, the project's plugins will probably be a subset
            // of
            // those specified in defaults.

            // TODO: share with inheritence assembler
            Map pluginMap = new TreeMap();
            for ( Iterator it = plugins.iterator(); it.hasNext(); )
            {
                Plugin plugin = (Plugin) it.next();
                pluginMap.put( constructPluginKey( plugin ), plugin );
            }

            List managedPlugins = pluginManagement.getPlugins();

            for ( Iterator it = managedPlugins.iterator(); it.hasNext(); )
            {
                Plugin def = (Plugin) it.next();
                String key = constructPluginKey( def );

                Plugin plugin = (Plugin) pluginMap.get( key );
                if ( plugin != null )
                {
                    mergePluginWithDefaults( plugin, def );
                }
            }
        }
    }

    private static String constructPluginKey( Plugin plugin )
    {
        return plugin.getGroupId() + ":" + plugin.getArtifactId();
    }

    private void mergePluginWithDefaults( Plugin plugin, Plugin def )
    {
        if ( plugin.getVersion() == null && def.getVersion() != null )
        {
            plugin.setVersion( def.getVersion() );
        }

        Map goalMap = new TreeMap();

        List pluginGoals = plugin.getGoals();
        if ( pluginGoals != null )
        {
            for ( Iterator it = pluginGoals.iterator(); it.hasNext(); )
            {
                Goal goal = (Goal) it.next();

                goalMap.put( goal.getId(), goal );
            }
        }

        List defGoals = def.getGoals();
        if ( defGoals != null )
        {
            for ( Iterator it = defGoals.iterator(); it.hasNext(); )
            {
                Goal defaultGoal = (Goal) it.next();

                Goal localGoal = (Goal) goalMap.get( defaultGoal.getId() );
                if ( localGoal == null )
                {
                    goalMap.put( defaultGoal.getId(), defaultGoal );
                }
                else
                {
                    Xpp3Dom goalConfiguration = (Xpp3Dom) localGoal.getConfiguration();
                    Xpp3Dom defaultGoalConfiguration = (Xpp3Dom) defaultGoal.getConfiguration();
                    localGoal.setConfiguration(
                        Xpp3Dom.mergeXpp3Dom( goalConfiguration, defaultGoalConfiguration ) );
                }
            }
        }

        plugin.setGoals( new ArrayList( goalMap.values() ) );

        Xpp3Dom pluginConfiguration = (Xpp3Dom) plugin.getConfiguration();
        Xpp3Dom defaultPluginConfiguration = (Xpp3Dom) def.getConfiguration();
        plugin.setConfiguration( Xpp3Dom.mergeXpp3Dom( pluginConfiguration, defaultPluginConfiguration ) );
    }

    private void injectDependencyDefaults( List dependencies, DependencyManagement dependencyManagement )
    {
        if ( dependencyManagement != null )
        {
            // a given project's dependencies should be smaller than the
            // group-defined defaults set...
            // in other words, the project's deps will probably be a subset of
            // those specified in defaults.
            Map depsMap = new TreeMap();
            for ( Iterator it = dependencies.iterator(); it.hasNext(); )
            {
                Dependency dep = (Dependency) it.next();
                depsMap.put( dep.getManagementKey(), dep );
            }

            List managedDependencies = dependencyManagement.getDependencies();

            for ( Iterator it = managedDependencies.iterator(); it.hasNext(); )
            {
                Dependency def = (Dependency) it.next();
                String key = def.getManagementKey();

                Dependency dep = (Dependency) depsMap.get( key );
                if ( dep != null )
                {
                    mergeDependencyWithDefaults( dep, def );
                }
            }
        }
    }

    private void mergeDependencyWithDefaults( Dependency dep, Dependency def )
    {
        if ( dep.getScope() == null && def.getScope() != null )
        {
            dep.setScope( def.getScope() );
        }

        if ( dep.getVersion() == null && def.getVersion() != null )
        {
            dep.setVersion( def.getVersion() );
        }
    }

}